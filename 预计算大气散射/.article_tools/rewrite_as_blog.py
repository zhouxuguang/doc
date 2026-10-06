"""Editorial revision: preserve derivations and shader excerpts, improve the blog narrative."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
path = ROOT/'预计算大气散射技术详解.md'
original = path.read_text()
if '我在 GNXEngine 中将预计算大气散射接入了独立 demo 和三维地球' in original:
    raise SystemExit('The blog revision is already applied.')
doc = original
changes = []

def paragraph(prefix, replacement):
    global doc
    parts = doc.split('\n\n')
    matches = [i for i, part in enumerate(parts) if part.startswith(prefix)]
    assert len(matches) == 1, (prefix, matches)
    parts[matches[0]] = replacement.strip()
    doc = '\n\n'.join(parts)
    changes.append(prefix)

def replace(old, new):
    global doc
    assert doc.count(old) == 1, (old, doc.count(old))
    doc = doc.replace(old, new, 1)
    changes.append(old)

def chapter_lead(number, text):
    global doc
    pattern = rf'(^## {number}\. [^\n]+\n)'
    doc, count = re.subn(pattern, lambda m: m.group(1)+'\n'+text.strip()+'\n', doc, count=1, flags=re.M)
    assert count == 1, number
    changes.append(f'Chapter {number} lead')

# Lead with the rendering problem and a real result, rather than writing logistics.
intro_end = doc.index('## 1. ')
doc = r'''# 预计算大气散射：从 Bruneton 推导到 GNXEngine 实践

把相机从地面拉到轨道，天空会从覆盖整个视野的蓝色穹顶，收缩成地球边缘的一圈薄光。同一时刻，远处地形的对比度也在改变：表面光沿途衰减，大气又把别处的光散射进视线。蓝天、日落和空气透视背后，其实是同一个光传输问题。

我在 GNXEngine 中将预计算大气散射接入了独立 demo 和三维地球。独立场景便于观察太阳、球体照明和散射阶数的变化；地球场景则把问题推进到大尺度坐标、空间相机、椭球地表和深度合成。下面这张轨道视角，就是这条预计算路径在引擎中的输出。

![GNXEngine 中的轨道视角与大气边缘](atmosphere_scattering_images/earth_orbit.png)

*GNXEngine 三维地球的轨道视角，使用 `LegacyPrecomputed`、五阶散射、曝光 5。大气边缘与地表空气透视由同一套传输模型计算，完整参数和其他视角见第 11 章。*

实时渲染的难点在于，每个像素沿视线积分一次还不够。一个散射点收到的光来自所有方向，这些光又可能经历过更早的散射。直接在每帧求解这样的嵌套积分，成本很快就会超过实时预算。

Bruneton 与 Neyret 的方法把高成本计算搬到了预计算阶段：利用球形大气的对称性，将不同位置、观察方向和太阳方向下的结果存进查找表。运行时通过少量纹理查询取回整条路径的贡献，再利用积分的分段性质得到有限距离空气透视。固定大气参数后，相机移动和太阳转向都变成对已有数据的查询。

这篇文章以 2008 年论文 **Precomputed Atmospheric Scattering** 为起点，以 Bruneton 的[新版 `functions.glsl` 核心函数文档](https://ebruneton.github.io/precomputed_atmospheric_scattering/atmosphere/functions.glsl.html)为算法依据，并穿插 GNXEngine 的 HLSL/C++ 实现。原论文帮助理解光路分解与预计算思路，新实现给出臭氧、太阳圆盘、纹理映射和运行时接口的具体定义。

沿着一条观察射线，整个方法可以串成一条链：**先求沿途衰减，再求各点产生的散射，把连续积分编码进 LUT，逐阶补齐间接光，最后与真实场景合成。** 三类查找表分别承担不同的工作：

| 查找表 | 保存什么 | 运行时解决什么问题 |
|---|---|---|
| 透射率 | 沿大气路径保留下来的光的比例 | 表面和太阳送到相机的光会衰减多少 |
| 散射 | 沿视线积累的大气光，按相函数约定编码 | 天空颜色与有限距离空气透视 |
| 辐照度 | 水平面收到的间接天空光 | 地面照明与预计算中的地面反射反馈 |

第 1—4 章从物理量和光路建立积分，第 5—7 章解释 LUT 与逐阶预计算，第 8—10 章把查询结果接到颜色管线和三维地球，第 11—13 章讨论效果、调试与工程取舍。原论文的逐图、逐式阅读对照放在附录，便于遇到记号差异时查阅。下文统一使用米作为长度单位，图中的高度按需要换算为千米。

'''+doc[intro_end:]
changes.append('Introduction')

# Give each major step a practical question and a reason to continue reading.
chapter_lead(1, '天空像素和地面照明经常都用 `float3` 保存，却代表两种不同的量。先把“某个方向有多亮”和“一个面总共收到多少光”分开，后面的相函数、角积分和 HDR 合成才有统一的含义。')
chapter_lead(2, '一张 LUT 能够供不同相机复用，前提是模型中有足够的对称性。Bruneton 选择球形壳层与径向密度，把空间变化压缩到高度，再用散射和吸收系数描述介质。这个选择同时决定了算法能表达哪些天气与地表反馈。')
chapter_lead(3, '散射点产生的光要先穿过一段大气才能到达相机，太阳光也要穿过大气才能照到散射点。两段衰减都依赖路径几何，所以先求出射线在哪里离开大气、在哪里撞到地面，再建立透射率查询。')
chapter_lead(4, '有了透射率，就可以沿观察射线逐点回答一个具体问题：太阳送到这里多少光，这一小段空气把其中多少散射回相机？单次散射的每个乘法因子，都能在这条光路上找到位置。')
chapter_lead(6, '太阳光经过一次散射后，本身就成了照亮其他空气和地面的光源。多次散射因此可以逐阶计算：用上一阶入射场产生新的局部源，再沿视线积分，得到下一阶天空。地面反射也放在这条递推链中。')
chapter_lead(7, '数学递推只规定“用哪一阶生成哪一阶”，GPU 还要解决结果写在哪里、旧数据什么时候可以覆盖，以及怎样把新贡献加到最终纹理。纹理复用、MRT 混合和逐层调度，都是这组依赖关系的具体实现。')
chapter_lead(8, '预计算完成后，运行时不再重做全方向积分。天空查询取出到边界的累计大气光；地面和物体则只需要相机到表面的有限一段。把这两种查询接到同一个传输解上，就能同时处理天空、太阳和空气透视。')
chapter_lead(9, '物理积分算出的光谱量还需要变成屏幕颜色。这一步会影响蓝天和日落的色调，也决定大气与已有 HDR 场景能否正确相加。先做一致的线性颜色转换，再统一曝光和显示，是合成公式继续成立的条件。')
chapter_lead(10, '独立 demo 可以把地表当作一个球，三维地球却有真实椭球、地形深度和百万米量级的坐标。接入时需要把两件事分开：场景几何负责决定看见哪个表面，球形 LUT 负责估计这条视线上的大气传输。下面按一个像素进入合成管线的顺序展开。')
chapter_lead(11, '下面从两个场景观察前面推导的结果。独立 demo 固定相机，改变太阳高度和散射阶数；三维地球固定太阳，改变观察高度。前者突出光路变化，后者检验空间相机、地表遮挡和有限距离合成能否连贯工作。')
chapter_lead(12, '调试这套算法时，最有用的是把误差定位到某一个运算：先确认单位与极限，再确认纹理映射，随后比较路径积分和散射阶次，最后观察颜色与画面。这样遇到地平线色带或暮光偏暗时，就有明确的排查顺序。')

for old, new in [
    ('## 1. 先统一物理量、方向和符号', '## 1. 从一个像素看到的光开始'),
    ('## 7. 预计算 Pass、累加方式与存储预算', '## 7. 把递推变成 GPU 上的预计算'),
    ('## 9. 光谱、XYZ、线性 sRGB 与最终显示', '## 9. 从光谱积分到屏幕颜色'),
    ('## 11. 用实际帧观察算法效果', '## 11. 在 GNXEngine 中观察天空与空气透视'),
    ('## 12. 验证：公式、数值、资源和视觉分层检查', '## 12. 把结果调对：从数值到画面'),
    ('### 6.5 当前 GNXEngine 的辐照度绑定差异', '### 6.5 一个容易混淆的输入：单阶与累计辐照度'),
    ('### 7.1 临时量和最终量必须分清', '### 7.1 临时纹理如何复用，最终纹理如何累加'),
    ('### 7.4 实际纹理显存，不用“约 8 MB”代替核算', '### 7.4 显存开销与透射率精度'),
    ('### 9.1 三个光谱样本不是三个显示颜色通道', '### 9.1 三个光谱样本如何转换成显示颜色'),
    ('### 9.3 GNXEngine 当前做了什么', '### 9.3 GNXEngine 的颜色处理与后续接入'),
    ('### 10.3 大尺度坐标的精度策略与边界', '### 10.3 大尺度坐标中的精度问题'),
    ('### 10.8 地球 HDR 合成的实际行为', '### 10.8 将空气透视合成到地球 HDR 场景'),
    ('### 12.2 本文已执行的 CPU 数值核验', '### 12.2 用双精度参考计算验证数学关系'),
    ('### 12.4 高阶收敛不能用后处理图代替', '### 12.4 怎样判断散射阶数已经足够'),
    ('### 12.5 GPU 与场景验证的下一层', '### 12.5 从 GPU 纹素回读到场景对比'),
]:
    replace(old, new)

# Preserve useful distinctions, expressing them through their physical consequences.
paragraph('源码的 `bottom_radius`', r'''
源码的 `bottom_radius`、`top_radius`、`rayleigh_scattering`、`mie_extinction` 分别对应 $r_b,r_t,\beta_{R,0}^s,\beta_{M,0}^e$。其中 `r` 是到星球中心的距离，高度要再减去 $r_b$。`transmittance_texture` 保存透射率，`scattering_texture` 保存按相函数约定编码的累计散射；这个区别决定了查询后还要执行哪些恢复运算。
''')
paragraph('原论文的公式很紧凑：', r'''
原论文的紧凑记号把位置、方向和波长参数省略了很多。阅读时，可以先把一个式子还原成光路：它在哪个点接收光，有没有做方向积分，有没有沿路径积累？下面的对照把这些含义展开；正文统一保留 $\lambda$，让单位和颜色处理始终可追踪。
''')
paragraph('从图 3 向代码翻译时，', r'''
图 3 展示的是密度随高度变化的形状，曲线的幅度还要与谱系数一起看。在某高度读出 0.5，表示该组分的参考系数取一半；臭氧在 25 km 取 1，则表示它达到自己的参考密度。两种组分的 1 并不对应相同的粒子数。代码先依据层宽选择系数，再把指数、线性项和钳位组合成曲线，因此调整层宽与调整系数会产生不同的密度剖面。
''')
paragraph('对于壳层内的起点，大气顶采用', r'''
对于壳层内的起点，大气顶采用正号根 $d_t=d_+(r_t)$；向下碰地的射线采用较近根 $d_b=d_-(r_b)$。最近边界距离由地面相交标志选择。求交时先检查判别式，再用 `SafeSqrt` 处理相切附近的微小负舍入误差，这样既能稳定计算切线，也能正确排除没有交点的射线。
''')
paragraph('式（22）贯穿单次散射', r'''
式（22）贯穿单次散射、多次散射和空气透视减法。$\nu$ 由两个固定世界方向点积得到，沿直线不变；$\mu$ 和 $\mu_s$ 则相对当前位置的天顶定义，随着路径推进不断更新。实现时可以复用前者，每个样本都重新计算后两者。
''')
paragraph('所以实际访问 501 个采样点，', '500 个区间对应 501 个采样点，首尾权重为一半。这个数量是实现中的质量选择：积分步长越大，越可能漏掉低空气溶胶的快速变化；地平线长路径与臭氧剖面的拐点也会改变误差。第 12.3 节会用更密的积分作对照。')
paragraph('式（28）中的有限线段仍必须', r'''
式（28）适用于在到达地面前结束的有限线段。`ray_r_mu_intersects_ground` 描述的是延长射线的边界分支，当前 $P\to Q$ 本身仍可以完全位于空气中。GNXEngine 的 `GetTransmittance` 按这两个分支取样，并逐通道执行 `min(value,1)`，限制插值和舍入带来的小幅越界。
''')
paragraph('图 5 与补图 A 应按', '图 5 和补图 A 中，商式能消掉尾段的关键是共用顶边界交点。实现时把边界分支从起点传到终点，两次查询才会沿同一条累计光路取值；若在终点重新选了另一条路径，剩余尾段也随之改变。')
paragraph('例如，只看一个波长、一个组分，', r'''
用一个简化的单波长样本来看这次乘法：令 $E_{\odot,\lambda}=1\,\mathrm{W\,m^{-2}\,nm^{-1}}$，两个透射率为 0.6 和 0.8，参考散射系数为 $2\times10^{-5}\,\mathrm{m^{-1}}$，密度为 0.5，相函数为 $0.1\,\mathrm{sr^{-1}}$，段长为 100 m。样本贡献就是 $\Delta L_\lambda=4.8\times10^{-5}\,\mathrm{W\,m^{-2}\,sr^{-1}\,nm^{-1}}$。完整积分将每个样本的这份贡献相加，并分别计算 Rayleigh 与 Mie 两种组分。
''')
paragraph('式（30）分离的是', r'''
式（30）把同一条直线积分中不随 $d$ 变化的角分布移到了积分外。$C_i$ 仍保留太阳方向对路径衰减和遮挡的影响，只是把解析相函数留到查询时计算。这样，LUT 保存较平滑的路径部分，太阳附近尖锐的 Mie 前向峰由真实 $\nu$ 上的解析函数恢复。
''')
paragraph('$E^{(0)}$ 是直接太阳辐照度，', r'''
$E^{(0)}$ 是直接太阳辐照度，后续作为地面边界源使用。式（33）近似小太阳圆盘在水平接收面上的平均余弦，地面处 $\mu_h=0$，过渡中心正好是水平线。式（31）则近似体积散射点看到的太阳可见比例；两个函数对应不同的接收方式，参考实现也分别使用它们。在高空，式（33）只保留水平面投影近似。
''')
paragraph('式（41）可分成两次压缩。', r'''
式（41）可分成两次压缩。先用地表太阳路径得到 $a$：太阳正上方时 $a=0$，水平时 $d_t=H$、$a=1$，到支持下限时 $a=A$。再用 $(1-a/A)/(1+a)$ 压入单位区间，其导数为 $-(1+1/A)/(1+a)^2$，在 $A>0$ 时单调，因而能由式（42）反解。地表在这里只是所有半径层共用的坐标标尺；各个散射样本的太阳透射率仍按自己的 $r_d,\mu_{s,d}$ 计算。
''')
paragraph('图 9 的密集样本条应读成', '图 9 的样本条标出实际参加预计算的太阳方向，可以直接看出地平线附近如何获得更多分辨率。它描述参数域上的采样分布。修改映射常数后，这些纹素代表的物理状态也会改变，因此预计算与运行时映射需要一起更新。')
paragraph('等价条件是三个单位向量的 Gram 行列式', r'''
同一约束还可以写成三个单位向量的 Gram 行列式 $1+2\mu\mu_s\nu-\mu^2-\mu_s^2-\nu^2\ge0$。相机通过单位向量点积产生的状态满足它，规则四维纹理却包含不可实现的组合。预计算解码将这些组合的 $\nu$ 钳到式（46）的最近边界，再构造对应方向，让冗余地址仍有稳定的插值数据。
''')
paragraph('因此，图 10 的空白区域不是', r'''
图 10 的空白区域对应不可实现的方向组合。规则纹理仍分配这些地址，解码时用合法边界填充；相机的实际查询则位于可实现域中。到了第 6.2 节，这个约束还会保证太阳方向的切向分量可以正确重建。
''')
paragraph('GNXEngine 的基础 `GetScattering`', 'GNXEngine 的 `GetScattering` 把这个地址计算直接写在 shader 中。下面保留函数体的取样过程，方便将两次三维查询与式（49）的四维插值逐项对应：')

# Make the implementation difference a concrete teaching case, not an audit disclaimer.
paragraph('数学函数里地面项使用传入的', '公式到了渲染图里，阶次就由纹理的内容决定了。这个位置尤其容易混淆：函数参数虽然叫 `irradiance_texture`，本轮需要的却是旧的单阶辐照度。GNXEngine 当前版本的密度 Pass 绑定如下：')
paragraph('表中的各 $E$ 表示', r'''
表中的 $E$ 均指当前运行路径生成的量。二阶地面项缺失会影响后续散射，因此第三轮即使输入阶次碰巧吻合，也已经沿着不同的递推结果继续计算。地面反照率为零时可以隔离这个差异，作为调试大气入射分支的起点。
''')
paragraph('要对齐参考递推，需要一起检查', r'''
对齐式（51）时，应让密度 Pass 的采样绑定和读状态屏障共同指向 `mDeltaIrradianceTexture`。这里的关键是让 GPU 读到 $E^{(n-2)}$：纹理名称、调度顺序与其中保存的阶次需要一致。下一章按这一标准依赖写出伪代码，后面的效果图则展示当前版本的输出。
''')
paragraph('“去相函数量与辐照度单位相同”', r'''
$C_R$ 与 $E$ 的单位相同，物理角色却不同。前者仍描述一条视线，只是把 $\mathrm{sr^{-1}}$ 的相函数因子移到了查询端；后者已经对半球来光做了投影积分。在 HLSL 中它们都可能是 `float3`，所以纹理调试时最好同时标出量的含义、阶次和相函数状态，才能解释某个通道的数值。
''')
paragraph('上面的 `irradiance=deltaE`', '这里 `irradiance=deltaE` 保留了单阶地面输入；`Esky` 专门负责运行时的累计间接照明。它们分开保存，既满足递推，也让纹理复用的时机更清楚。GNXEngine 当前绑定的具体差异见第 6.5 节。')
paragraph('这张表解释的是当前步骤列表', r'''
游标可以在一个阶段中间暂停，下一帧从同一位置继续；整张最终 LUT 应在全部步骤完成后投入使用。调度成本也取决于每个步骤内部做了多少计算：$256\times128\times32$ 的密度表有 1,048,576 个纹素，每个纹素计算 512 个方向，一次完整 density 阶段约有 5.37 亿次方向样本循环，虽然只录制了 32 个 draw。因此每帧 24 步是工作量拆分策略，后续还可以按 GPU 时间调整预算。
''')
paragraph('资源屏障负责让采样看到', '排查资源问题时，可以沿着一个消费者的输入追踪四件事：绑定对象、对象当前保存的量、访问状态，以及写入附件的 load 和混合方式。屏障保证数据可见，阶次和量的含义由绑定与生命周期保证。这两条线一起检查，才能解释“资源访问正常，数值却不对”的情况。')
paragraph('`RunPrecomputeStep` 的间接辐照度分支', '间接辐照度分支将 UBO 阶次设为 `step.order - 1`。例如列表处于二阶轮次时，该 Pass 要从一阶天空生成一次间接辐照度；列表中的轮次编号与积分函数的输入阶次由此对应起来。')
paragraph('`mPrecomputed` 在最后步骤', '`mPrecomputed` 在最后一步和状态转换录制完成后置位。同一队列上的后续渲染依靠提交顺序消费结果；跨队列使用和 CPU 纹理回读则需要相应的完成同步。录制完成与 GPU 执行完成分别对应这两个时刻。')
paragraph('本文的 CPU 量化例子中，', r'''
用 CPU 量化观察 FP16 格式：$\tau=10$ 时透射率的相对误差约为 0.0414%，$\tau=15$ 时约为 2.576%，$\tau=18$、20 时舍入成零。长路径越接近下溢，商式越难保留有效比例。将透射率改为 FP32 只增加约 128 KiB 纹理数据，是一个成本很小、值得优先比较的精度选择；具体 GPU 后端的非正规数行为还需要回读验证。
''')
paragraph('GNXEngine 保留 `COMBINED_SCATTERING_TEXTURES`', 'GNXEngine 保留了 `COMBINED_SCATTERING_TEXTURES` 与 `GetExtrapolatedSingleMieScattering` 分支，当前这条路径使用独立单次 Mie 纹理，直接读取完整三通道。最终 alpha 虽然也写入 Mie 红值，运行时是否重建仍由编译宏和绑定决定。独立存储多占 8 MiB，换来更直接的谱通道数据。')

# Keep runtime limitations where they explain a practical rendering decision.
paragraph('因此，论文说“一次散射能处理遮挡”时，', '因此，这个阴影处理由两个部分组成：场景几何提供太阳可见区间，参考积分提供区间内的散射贡献。连续单段阴影可以套用这里的减法；多段阴影需要保存各段的位置，高阶地形反馈则需要更丰富的源场表示。')
paragraph('GNXEngine demo 用 `GetSphereShadowInOut`', 'GNXEngine demo 用 `GetSphereShadowInOut` 求球体太阳阴影锥的进出距离，将区间压缩为 `shadow_length`，并在太阳接近地平线时淡出光柱。这沿用了前缀或后缀阴影的近似。地球合成当前传入 0，地形体积阴影可以作为后续单独接入的一层。')
paragraph('散射和吸收都依赖波长。计算', r'''
散射和吸收都依赖波长。三个结果 $L_{680\,\rm nm},L_{550\,\rm nm},L_{440\,\rm nm}$ 代表长、中、短波处的光谱采样；线性 sRGB 的每个通道则是宽光谱经过颜色匹配函数积分后的坐标。两者虽然都能装进 `float3`，中间仍需要颜色转换。XYZ 到 RGB 的矩阵甚至带有负系数，反映的是颜色基底的变化。
''')
paragraph('因此本文截图体现', r'''
当前画面将三波长结果直接送入引擎显示链路，这一选择简化了接入，也留下了与完整光谱颜色之间的差异。曝光负责亮度尺度，白点负责颜色平衡，而式（68）的积分负责光谱到显示颜色的转换。日落长路径尤其适合比较这些处理各自带来的变化。
''')
paragraph('当前 UBO 提供 `white_point_pad`', '当前 Legacy 天空、demo 与 planet 输出尚未使用 UBO 中的 `white_point_pad`。后续接入参考颜色转换时，应同时处理太阳直射、天空入散射和材质光照，使它们进入同一颜色空间和尺度，再统一应用白点与曝光。')
paragraph('`AtmosphereComponent` 支持', '`AtmosphereComponent` 中已有 `LegacyPrecomputed` 和 `SkyAtmosphere` 两条路径。下面的初始化、预计算和合成都围绕前者展开，独立 demo 与三维地球也使用同一算法选择。')

# Let the screenshots illustrate the theory rather than narrating their capture process.
paragraph('以下效果图来自 GNXEngine 的实际帧输出，', '为了观察光路与阶数变化，下面统一使用 `LegacyPrecomputed`、曝光 5 和 2560×1440 输出，截图前等待 LUT 完成。独立 demo 隐藏调参面板，地球视图在第 180 帧取样，减小瓦片加载和 LOD 变化对画面的影响。具体相机与太阳参数写在图注中。')
paragraph('本文代码对照以 GNXMapEngine 主仓库', '代码对应 GNXMapEngine 主仓库 `a16cf56`、GNXEngine 子模块 `0583671`，画面来自 macOS Metal 后端。这组效果展示当前实现；有关地面递推输入和颜色转换的改进点，分别在第 6.5、9.3 节说明。')
paragraph('日间图的天空从上方', '先看日间图中的近景球体：它接收太阳直射和天空照明，表面反射再经过相机到球体的空气路径。再看远处地面：蓝色材质逐渐失去对比，向该方向的路径散射颜色靠拢。天空从天顶深蓝过渡到地平线浅色，则反映了密度、路径长度和散射角共同变化。')
paragraph('太阳斜穿大气时低空光路变长，', '太阳靠近地平线时，直射光斜穿低空大气，较短波长被更强地移走，太阳和受它照亮的表面逐渐偏暖。与此同时，天空仍对整条视线上的采样点求和：不同高度的太阳衰减、观察路径衰减和气溶胶角分布共同塑造地平线色带。第 4 章的“两段光路”在这里可以直接对应到画面变化。')
paragraph('这组对照展示的是现有引擎的阶数设置效果。', '这组图适合观察暮光亮度与色带的变化。若要测量各阶的贡献，可以沿同一组视线读取色调映射前的 HDR 值，按第 12.4 节比较最后一阶占累计光的比例；当前地面输入差异则按第 6.5 节先行处理。')
paragraph('地球接入使用 `EarthAtmospherePreset.cpp`', '三维地球使用 `EarthAtmospherePreset.cpp`：底半径仍为 6360 km，顶半径为 6460 km，对应 100 km 大气壳。独立 demo 使用 60 km 壳层，两组图展示的是同一算法在不同边界参数与场景中的应用。')
paragraph('全球图展示黑色太空背景', '全球视角把真实椭球遮挡与球形大气查询放在同一画面中。地图瓦片提供地表影像，场景几何决定哪些像素被地球挡住，大气合成负责边缘和地表前方的路径贡献。太空背景、地球轮廓和大气薄层在这里需要保持一致，正好对应第 10 章的接入流程。')
paragraph('大气边缘对应长斜向光路，', '轨道斜视时，靠近边缘的射线沿大气壳走过很长距离，形成可见的蓝色薄层；完全避开大气的方向则保留太空背景。地表颜色还包含瓦片影像和统一后处理，因此观察边缘时，重点看它与地表轮廓的衔接，以及相机升高后的连续变化。')
paragraph('低空图能更直接观察深度重建', '低空视角把注意力拉回有限距离空气透视：近处地形保留对比，远处逐渐融入大气颜色，轮廓自然接入天空。这里的每个地形像素都先由深度确定真实终点，再用大地高度和距离构造代理路径。地平线色带或随相机移动的跳变，可以沿第 10.7 节的端点高度、代理余弦和边界分支逐项定位。')

# Local launch commands are work records, not part of the explanatory narrative.
launch_start = doc.index('地球启动参数采用现有 `GNX_MAP_*` 接口')
launch_end = doc.index('### 11.5 ', launch_start)
launch_record = doc[launch_start:launch_end]
doc = doc[:launch_start]+doc[launch_end:]
changes.append('Remove local launch commands')

# Put the sampling example next to the parameterization it motivates.
comparison_start = doc.index('### 11.5 论文中的参数化对比')
comparison_end = doc.index('## 12. ', comparison_start)
comparison = doc[comparison_start:comparison_end]
comparison = comparison.replace('### 11.5 论文中的参数化对比', '### 5.9 距离参数化为什么能改善空气透视', 1)
comparison = comparison.replace('用户提供论文的 Figure 3 比较了线性观察余弦与基于边界距离的映射。以下两图直接提取自原 PDF 的该图，保留原始图像，分别对应图注中的左图与右图；它们不是 GNXEngine 输出。',
    '纹理映射的价值最终要体现在插值上。Bruneton 与 Neyret 在原论文 Figure 3 中，用同一个场景比较线性观察余弦与距离参数化：前者在空气透视中出现伪影，后者让两个累计查询更好地区分真实路径的变化。')
comparison = comparison.replace('*图 24：', '*论文 Figure 3 左图：', 1).replace('*图 25：', '*论文 Figure 3 右图：', 1)
comparison = comparison.replace('[用户提供的论文]', '[原论文]')
comparison = comparison.replace('此图用于说明采样策略的作用；新版具体映射以第 5 节为准，不把旧论文的指数太阳映射混入新版公式。',
    '距离坐标把采样分辨率集中到低空长路径变化明显的区域。本文采用的具体正反映射见第 5.2—5.5 节。')
comparison = comparison.replace('最后一行是用**新版**距离端点映射重新计算的示例，数值与论文所说明的约 0.11 接近，但没有把旧论文的所有坐标公式照搬过来。线性余弦取样把大部分方向样本分配给并不敏感的区域；距离坐标则将低空长路径的明显变化展开到更大的纹理区间。原图改善的是 LUT 插值与差分中的采样表现，不是“距离坐标让真实天空增加了散射”。',
    '最后一行采用新版距离端点映射，变化约为 0.109，与论文示例的约 0.11 接近。物理积分保持不变，改变的是纹素怎样分辨这些积分：线性余弦把这条 100 km 路径压在很小的坐标差里，距离参数化则将它展开。第 8.3 节会推导两次累计查询的减法，这里已经能看出采样分配为何影响其数值稳定性。')
doc = doc[:comparison_start]+doc[comparison_end:]
insertion = doc.index('## 6. ')
doc = doc[:insertion]+comparison+doc[insertion:]
doc = doc.replace('第 11.5 节数值例子', '第 5.9 节数值例子')
changes.append('Move paper interpolation comparison to 5.9')

# Turn validation reporting into a useful debugging method.
paragraph('最容易定位的错误往往不是', r'''
排查时，先让每个中间量带着单位走一遍。式（23）的 $\beta d$ 无量纲，式（29）的被积项是每米的辐亮度增量，式（56）经过方向积分后是辐照度。只要某一步单位接不上，就可以在复杂天空颜色出现之前定位遗漏的系数、段长或相函数。
''')
paragraph('相函数归一化是能量分配约束，', r'''
相函数归一化可以用一个常量各向同性入射场检查：$\int pL\,\mathrm d\Omega=L$。无论峰值集中在前向还是均匀分布，总方向权重都应为 1；多出来的 $4\pi$ 通常意味着归一化常数或立体角权重使用错误。
''')
paragraph('为检查公式与参数化的自洽性，', '我用双精度参考计算检查正反映射与积分恒等式，随机样本固定种子，便于重复比较。下表关注的是公式和代数实现；它为 GPU 纹素回读提供基准。')
replace('| 检查 | 方法与样本 | 本次结果 |', '| 数学关系 | 计算方法 | 参考结果 |')
replace('光学厚度差为 0（本次双精度结果）', '光学厚度差为 0（该双精度样本）')
paragraph('这些很小的映射误差说明', r'''
正反映射的误差接近双精度舍入尺度，说明几何编码与解码相容。接着移到 GPU，还要分别评估 FP32 算术、FP16 存储、纹理插值和积分步长。有限散射测试在已知源场上验证式（63）；实际 `GetSkyRadianceToPoint` 的 Mie 地平线淡出则属于查询端的另一层处理。
''')
paragraph('本文还在 $h=1$ km', r'''
在 $h=1$ km 处，将 500 区间与 20,000 区间的密度积分比较，天顶方向的 Rayleigh 相对差约为 $1.81\times10^{-5}$，Mie 约为 $8.05\times10^{-4}$。水平和切线方向的误差分布又不同，臭氧剖面的拐点也会影响梯形积分。这说明收敛检查应选择不同高度与方向，而不是只增加一个全局步数后观察画面是否更亮。
''')
paragraph('验证应先采用零地面反照率', r'''
可以先设平均地面反照率为零，观察纯大气分支的 1—5 阶变化；再加入地面反射，单独检查 $n=2$ 的直接地面路径。对白天、日落和暮光选择固定视线，这样每次变化都能对应到明确的路径来源。GNXEngine 当前版本需要先对齐第 6.5 节的输入，再与标准递推做定量比较。
''')
paragraph('可以对少量确定纹素回读 GPU 结果，', 'GPU 对照可以从少量确定纹素开始：先回读没有太阳方向和递推依赖的透射率，再比较单次 Rayleigh/Mie、密度源、间接辐照度和逐阶辐亮度，最后进入颜色转换与显示。每完成一层再进入下一层，能把差异留在最小的计算范围内。')
paragraph('本次真实帧采集日志确认', '')
paragraph('视觉检查主要覆盖天空方向连贯性', '最后回到画面，沿着白天到日落、低空到轨道两条变化线观察天空连续性、实体遮挡、太阳位置、地表空气透视与边缘接缝。固定曝光、相机、太阳和瓦片状态，再比较前后结果，画面中的差异才容易与某个实现改动对应起来。')

# End on engineering judgment, rather than an approval or delivery checklist.
start = doc.index('## 13. 工程改进项与取舍')
end = doc.index('## 附录 A：', start)
doc = doc[:start]+r'''## 13. 实现后的取舍与下一步

接到两个场景之后，后续工作可以分成三层：先让每个纹理值代表正确的物理量，再评估几何和视觉近似，最后按运行成本选择质量。这个顺序也决定了哪些改进最值得先做。

### 13.1 先保证递推和颜色语义一致

当前版本优先要处理的是第 6.5 节的单阶辐照度输入。它影响的是光路事件本身，增加纹理尺寸或散射阶数都会继续放大原有递推，而不会补回缺失的二阶地面贡献。太阳方向映射也应让正反函数共享精确端点 $A$，在修改后重建 LUT，保持纹素与物理方向的对应。

精度方面，透射率 FP32 是一个成本很小的选择：它改善长路径商式的动态范围，额外数据只有约 128 KiB。颜色方面，可以先接入参考三波长转换因子，再比较多波长 CIE 预积分。太阳、天空、材质照明和已有 scene color 需要落到一致的线性空间与尺度，最后统一处理曝光、白点和显示。

已有场景颜色也带来一个实际合成问题：有深度表面、缺失地面回退和太空背景，使用的是不同来源的边界光。分别按式（64）确认透射率与曝光位置，才能让星空经过大气时衰减，让地表回退与实际地形保持相同亮度尺度。

### 13.2 让几何近似与目标场景相匹配

球形 LUT 很适合复用，但三维地球的椭球代理仍是近似。低空远山和轨道边缘应分别观察，并回读真实大地高度、代理端点高度和视线距离。如果目标需要严格的椭球密度场，就需要扩展参数化或使用局部积分；端点拟合更适合在现有球形模型上保持视觉与几何的连续性。

阴影也是类似的取舍。单一 `shadow_length` 接口成本低，能表达约定位置的连续阴影段；地形光柱需要区间位置或沿视线的可见度采样。直射太阳阴影与间接多次散射的遮挡应分别处理，才能保留阴影中来自其他方向的光。

### 13.3 将质量提升放在可控的成本内

增加纹理分辨率和积分样本数，应针对已定位的误差。更高的 $N_\nu$ 可以改善高阶散射角分布的插值；单次 Mie 尖峰已有解析相函数恢复，扩大全部四维数据的成本未必划算。先比较敏感方向的积分收敛和纹素回读，再决定增加哪个轴的分辨率。

预计算调度还可以从每帧 24 步发展为按 GPU 时间控制预算。若要运行时修改气溶胶或平均地面颜色，可以双缓冲最终 LUT：后台完整生成新表，完成同步后一次切换。缓存键应包含密度与光谱参数、半径、阶数、纹理尺寸、映射版本、格式和颜色模式，这样同一算法的不同配置也能安全复用。

这套方法给引擎留下了一个很有用的划分：介质参数决定预计算积分，相机和太阳决定查询位置，真实几何决定光路终点，颜色管线决定怎样显示结果。把这几层连起来，同一个传输模型就能贯穿近景球体、低空远山和轨道上的大气边缘；后续的精度与效果改进，也都有各自明确的位置。

'''+doc[end:]
changes.append('Rewrite engineering conclusion')

# Credits identify sources; the publication should not address a drafting assistant.
replace('本文本地材料：[预计算大气散射.pdf](预计算大气散射.pdf)。', '论文：[预计算大气散射.pdf](预计算大气散射.pdf)。')
replace('参考源码版权为 Copyright (c) 2017 Eric Bruneton；本地快照保留完整许可证。GNXEngine 摘录用于解释用户自己的实现。',
        '参考源码版权为 Copyright (c) 2017 Eric Bruneton，使用与分发应遵循其 BSD-3-Clause 许可证。GNXEngine 代码片段用于说明本文的引擎实现。')
replace('实时大气积分的工程背景；不将其单次散射路径替代为本文的逐阶递推。', '介绍实时大气路径积分，可与本文的预计算与多阶方法对照阅读。')
replace('新版三波长颜色转换近似所引用的研究；颜色准确性不能仅凭一组美观截图判断。', '讨论天空模型的定性与定量比较，也是理解三波长颜色转换近似的重要资料。')

# Every numbered derivation and algorithm excerpt must survive the editorial pass.
display = lambda value: re.findall(r'\$\$(.*?)\$\$', value, re.S)
assert display(doc) == display(original), 'A numbered derivation changed.'
code = lambda value: re.findall(r'```(hlsl|cpp|text)\n(.*?)```', value, re.S)
assert code(doc) == code(original), 'A shader or scheduling excerpt changed.'
images = lambda value: set(re.findall(r'!\[[^\]]*\]\(([^)]+)\)', value))
assert images(doc) == images(original), 'An existing figure was lost.'
assert not any(token in doc for token in ['本次文章', '用户提供', '结果见 JSON', '.article_tools/', '/Users/zhouxuguang/'])
doc = re.sub(r'\n{3,}', '\n\n', doc).rstrip()+'\n'
backup = ROOT/'.article_tools/revision5_before'
backup.mkdir(exist_ok=True)
backup.joinpath(path.name).write_text(original)
ROOT.joinpath('.article_tools/地球效果采集启动参数.md').write_text('# 地球效果采集启动参数（写作工作记录）\n\n'+launch_record)
path.write_text(doc)
report = {'editorial_changes': len(changes), 'changes': changes,
          'numbered_derivations_preserved': len(display(doc)),
          'algorithm_code_blocks_preserved': len(code(doc)),
          'unique_images_preserved': len(images(doc)),
          'paper_interpolation_section': '5.9', 'local_capture_commands_archived': True}
ROOT.joinpath('.article_tools/qa/blog_editorial_revision.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k: v for k, v in report.items() if k != 'changes'}, ensure_ascii=False))
