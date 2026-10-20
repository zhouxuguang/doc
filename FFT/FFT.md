## 一、FFT的基本原理

### 1. FFT的定义

离散傅里叶变换（Discrete Fourier Transform，缩写为DFT），是傅里叶变换在时域和频域上都呈离散的形式，将信号的时域采样变换为其DTFT的频域采样。

FFT是一种高效实现DFT的算法，称为快速傅立叶变换（Fast Fourier Transform，FFT）。它对傅里叶变换的理论并没有新的发现，但是对于在计算机系统或者说数字系统中应用离散傅立叶变换，可以说是进了一大步。

在1965年，Cooley和Tukey发表了快速傅里叶变换算法。事实上FFT早在这之前就被发现过了，但是在当时现代计算机并未问世，人们没有意识到FFT的重要性。一些调查者认为FFT是由Runge和König在1924年发现的。但事实上高斯早在1805年就发明了这个算法，但一直没有发表。

### 2. FFT的算法思想
快速傅立叶算法的最核心思想就是分治法的思想，即把一个复杂的问题，分解为一个小的类似问题进行求解，然后再把一个个问题的解进行合并。按照这个思想，可以用递归的方法来实现，但是在计算机编程中，我们通常采用迭代的方法来实现。这也就是我们常说的蝶形运算。

### 3. FFT的推导过程
我们首先来看FFT怎么将数据进行划分，也就是分治的思想。一般的，将一个长度为N的序列，分成两个长度为N/2的子序列。然后将其中一个子序列翻转，然后进行相乘，最后再进行合并。这个过程就是蝶形运算的过程。

![图1 按n的奇偶将序列分为两个N/2点子序列](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E5%A5%87%E5%81%B6%E5%88%92%E5%88%86.png)

<p align="center">图1  按n的奇偶将序列分为两个N/2点子序列</p>

根据上图中的定义，序列x(n)的N点DFT可以表示为如下：

![图2 序列前一半的N/2点DFT推导](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E5%89%8D%E4%B8%80%E5%8D%8ADFT%E6%8E%A8%E5%AF%BC.jpg)

<p align="center">图2  序列前一半的N/2点DFT推导</p>

那么序列x(n)后一半的DFT可得：

![图3 序列后一半的N/2点DFT推导](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E5%90%8E%E4%B8%80%E5%8D%8ADFT%E6%8E%A8%E5%AF%BC.jpg)

<p align="center">图3  序列后一半的N/2点DFT推导</p>

结合前面手写稿中的推导，可以得到：

![图4 折半后的DFT与蝶形运算表达式](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E6%8A%98%E5%8D%8A%E7%9A%84DFT.png)

<p align="center">图4  折半后的DFT与蝶形运算表达式</p>

下面引入蝶形符号来表示这个过程，因为蝶形运算的外观像一只蝴蝶，所以又称蝶形图。蝶形运算符号的一般形式如下图所示，其中a、b为输入，c为旋转因子，两路输出分别为a+bc和a−bc。

![图5 蝶形运算符号](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E8%9D%B6%E5%BD%A2%E8%BF%90%E7%AE%97%E7%AC%A6%E5%8F%B7.png)

<p align="center">图5  蝶形运算符号</p>

图4的蝶形运算表示为如下图所示：

![图6 由两个N/2点DFT合成N点DFT的蝶形图](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/DFT%E5%88%86%E8%A7%A3%E8%9D%B6%E5%BD%A2%E5%9B%BE.png)

<p align="center">图6  由两个N/2点DFT合成N点DFT的蝶形图</p>

### 4. 蝶形图
下面以8点DFT为例，画出蝶形图：

![图7 8点DFT的一次分解](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/8%E7%82%B9DFT%E7%9A%84%E4%B8%80%E6%AC%A1%E5%88%86%E8%A7%A3.jpg)

<p align="center">图7  8点DFT的一次分解</p>

图中把8点DFT拆成两个4点DFT：①为偶数序列x(2n)构成的N/2点DFT，②为奇数序列x(2n+1)构成的N/2点DFT。两个子DFT的输出分别记为X₁(k)和X₂(k)，其中X₂(k)在参与合并前需要乘以旋转因子W_N^k。上半部分输出X(0)~X(3)，对应X(k)=X₁(k)+W_N^kX₂(k)；下半部分输出X(4)~X(7)，对应X(k+N/2)=X₁(k)−W_N^kX₂(k)，图中标注的"−1"即表示这一负号，因此每个蝶形只需要一次复数乘法。

由于每个N/2点DFT还可以继续按同样的方式一分为二，反复分解直到只剩2点DFT，就得到了完整的FFT流图。8点FFT共需log₂8=3级分解，下图给出了完整的蝶形流图：

![图8 8点FFT的完整蝶形流图](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/8%E7%82%B9FFT%E8%9D%B6%E5%BD%A2%E6%B5%81%E5%9B%BE.jpg)

<p align="center">图8  8点FFT的完整蝶形流图</p>

可以看出，每一级都由N/2=4个蝶形组成，3级共12个蝶形，即12次复数乘法和24次复数加法；而直接计算8点DFT需要64次复数乘法。推广到N点，FFT的运算量由O(N²)降为O(Nlog₂N)。

另外，流图左侧的输入并不是自然顺序，而是x(0)、x(4)、x(2)、x(6)、x(1)、x(5)、x(3)、x(7)，这正是自然序号用二进制表示后按位倒置（bit-reversal）的结果，例如3=(011)₂倒置为(110)₂=6。因此在迭代实现时，需要先对输入序列做码位倒置，再逐级进行蝶形运算，最后按自然顺序输出结果。

从完整的8点FFT的蝶形图还可以看出一个规律：每一级蝶形运算的旋转因子W_N^k都是固定的，即W_8^0=1, W_8^1=e^(−2πi/8), W_8^2=e^(−4πi/8)=W_8^1², W_8^3=e^(−6πi/8)=W_8^1³。因此，在迭代实现时，可以预先计算出所有旋转因子，并存储在一个表中，在蝶形运算时直接查表即可。另外旋转因子的指数也是由规律，可以计算出来，这样在编程时不至于弄错。指数计算如下：

![图9 第L级旋转因子的一般规律](https://raw.githubusercontent.com/zhouxuguang/doc/3cb45d43a316a0b465c2b8a63378426ca5757efb/FFT/img/%E7%AC%ACL%E7%BA%A7%E6%97%8B%E8%BD%AC%E5%9B%A0%E5%AD%90.png)

<p align="center">图9  第L级旋转因子的一般规律</p>

设N=2^M，则第L级（L=1,2,…,M）的蝶形运算所用到的旋转因子可以统一写成W_N^p=W_{2^L}^J，其中J=0,1,…,2^(L−1)−1。由2^L=2^M·2^(L−M)=N·2^(L−M)可得W_N^p=W_{N·2^(L−M)}^J=W_N^(J·2^(M−L))，于是旋转因子的指数为

p = J·2^(M−L),  J = 0,1,…,2^(L−1)−1

有了这个通式，就不必为每级单独推导旋转因子：只要知道当前的级数L和该级第J个蝶形，就能直接算出对应的W_N^p，编程时按级循环、组内按J循环即可。这也正是下面迭代实现时的核心公式。

## 二、FFT的实现步骤

### 1. 初始化
初始化一半在构造函数中进行，我的实现主要做以下三件事：
1、初始化旋转因子表 
2、计算蝶形运算的级数 
3、计算按位反转的表

### 2. 迭代实现
迭代实现主要做以下三件事：
1、按位反转输入序列
2、蝶形运算
3、输出结果

### 3、实现
实现就是最普通的蝶形运算，没有做任何优化，可以说就是教科书上的算法实现，帮助自己更深刻的理解FFT。

#### 1. 头文件 fft.h
```cpp
using cd = std::complex<double>;

class FFT
{
public:
    FFT(int n);
    
    std::vector<cd> forward(const std::vector<cd>& x) const;

    std::vector<cd> inverse(const std::vector<cd>& X) const;
    
private:
    int mN = 0;
    int mStages = 0;
    std::vector<uint32_t> mReverseTable;
    std::vector<cd> mTw;
    void buildTwiddle();
};
```

#### 2. 源文件 fft.cpp
```cpp
#include "FFT.h"

uint32_t ReverseBitsLoop(uint32_t x, uint32_t bits)
{
	if (bits == 0)
		return 0;

	uint32_t result = 0;
	for (uint32_t i = 0; i < bits; ++i)
	{
		result = (result << 1) | (x & 1u);
		x >>= 1;
	}
	return result;
}

FFT::FFT(int n)
{
    mN = n;
    mTw.resize(mN / 2);
	buildTwiddle();

	// 计算蝶形运算的级数
	int stages = 0;
	while ((1 << stages) < n) ++stages;
	mStages = stages;

	// 计算反转表
	mReverseTable.reserve(mN);
	for (int i = 0; i < mN; i ++)
	{
		mReverseTable.push_back(ReverseBitsLoop(i, mStages));
	}

}

void FFT::buildTwiddle()
{
    // 构造旋转矩阵，根据旋转矩阵的周期性，这里只需要存储n个数值就可以了
    const double PI = std::acos(-1.0);
    
    for (int i = 0; i < mN / 2; i ++)
    {
        double theta = -2.0 * PI * i / mN;
        mTw[i] = cd(cos(theta), sin(theta));
    }
}

std::vector<cd> FFT::forward(const std::vector<cd>& x) const
{
    // 1、根据原始序列位串反转表的计算，并将原始序列位串反转
	std::vector<cd> dst(mN);
	for (int i = 0; i < mN; i++)
	{
		dst[i] = x[mReverseTable[i]];
	}

	cd* data = dst.data();

	// 2、蝶形运算
	for (int s = 1; s <= mStages; ++s)
	{
		uint32_t blockLength = 1 << s; // 每一级的蝶形块的长度，例如，
										// 第1级就是相邻的两个元素做蝶形运算，那么蝶形块的长度就是2，第二级就是4，第三级就是8

		uint32_t halfBlockLength = blockLength >> 1;  // 每一级的蝶形块的长度的一半，也是两个蝶形运算输入数据的索引“距离”

		// 每一个块做蝶形运算
		for (uint32_t start = 0; start < mN; start += blockLength)
		{
			cd* low = data + start;
			cd* high = low + halfBlockLength;

			for (uint32_t j = 0; j < halfBlockLength; j ++)
			{
				const cd u = low[j];
				const cd v = high[j] * mTw[j * pow(2, mStages - s)];

				low[j] = u + v;
				high[j] = u - v;
			}
		}
	}
    return dst;
}

std::vector<cd> FFT::inverse(const std::vector<cd>& X) const
{
	// 1、根据原始序列位串反转表的计算，并将原始序列位串反转
	std::vector<cd> dst(mN);
	for (int i = 0; i < mN; i++)
	{
		dst[i] = X[mReverseTable[i]];
	}

	cd* data = dst.data();

	// 2、蝶形运算
	for (int s = 1; s <= mStages; ++s)
	{
		uint32_t blockLength = 1 << s; // 每一级的蝶形块的长度，例如，
		// 第1级就是相邻的两个元素做蝶形运算，那么蝶形块的长度就是2，第二级就是4，第三级就是8

		uint32_t halfBlockLength = blockLength >> 1;  // 每一级的蝶形块的长度的一半，也是两个蝶形运算输入数据的索引“距离”

		// 每一个块做蝶形运算
		for (uint32_t start = 0; start < mN; start += blockLength)
		{
			cd* low = data + start;
			cd* high = low + halfBlockLength;

			for (uint32_t j = 0; j < halfBlockLength; j++)
			{
				const cd u = low[j];
				const cd v = high[j] * std::conj(mTw[j * pow(2, mStages - s)]);

				low[j] = u + v;
				high[j] = u - v;
			}
		}
	}

	double divFactor = 1.0 / mN;
	for (int i = 0; i < mN; i++)
	{
		dst[i] *= divFactor;
	}

	return dst;
}
```

以上代码的完整工程已托管在 GitHub 仓库 NumericalAnalysis 中，可直接克隆后编译运行：

- 仓库地址：<https://github.com/zhouxuguang/NumericalAnalysis>
- 对照实现 [DFT.cpp](https://github.com/zhouxuguang/NumericalAnalysis/blob/main/DFT.cpp)：不做分解、直接按定义计算 X(k)=Σx(n)W_N^(kn)（模 N 处理旋转因子的周期性），复杂度为 O(N²)，用于与 FFT 的结果相互验证；文件中的TestDFT()对一个8点实序列做正变换后再反变换，可直观看到频谱与还原结果。

## 参考文献

1. 快速傅里叶变换（FFT）课程讲义[EB/OL]. 西安电子科技大学. <https://web.xidian.edu.cn/kywang/files/20171213_190241.pdf>
2. OI Wiki. Fast Fourier Transform[EB/OL]. <https://en.oi-wiki.org/math/poly/fft/>
3. 快速傅里叶变换（FFT）视频讲解[EB/OL]. 哔哩哔哩. <https://www.bilibili.com/video/BV1ke2aBGErz>
4. zhouxuguang. NumericalAnalysis[CP/OL]. GitHub. <https://github.com/zhouxuguang/NumericalAnalysis>

> 说明：第 1 篇为本文第 3 节推导过程的主要参考，第 2 篇侧重迭代实现与码位倒置，第 3 篇为配套视频讲解，第 4 篇为本文对应的代码仓库。