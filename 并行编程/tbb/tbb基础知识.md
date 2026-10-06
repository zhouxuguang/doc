#! https://zhuanlan.zhihu.com/p/677652569
# intel TBB基础知识

以前简单用过tbb的并行，但是只是浅尝辄止，这次稍微深入些，学习的资料是参考https://www.bilibili.com/video/BV1gu411m7kN/。
小彭老师的c++高性能课程。下面的代码示例也是基于小彭老师的代码来学习，在此，向小彭老师表示感谢，提供了质量非常高的干货可以供我们学习。

## 一、并行for
### 1、区间版本

```cpp
template<typename Range, typename Body>
void parallel_for( const Range& range, const Body& body );
```
例子如下：并行计算sin
```cpp
tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
[&] (tbb::blocked_range<size_t> r)
{
    for (size_t i = r.begin(); i < r.end(); i++) {
        a[i] = std::sin(i);
    }
});
```
range指定并行计算的范围，body指定并行执行的计算任务，r是当前这个任务的区间。

### 2、面向初学者的版本
```cpp
template <typename Index, typename Function>
void parallel_for(Index first, Index last, const Function& f);
```

例子如下：
```cpp
tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i) 
{
    a[i] = std::sin(i);
});
```
这个只能按照单个元素的计算作为一个独立的任务让tbb去调度，对编译器的simd的优化用不上。

### 3、迭代器的版本
```cpp
template<typename Iterator, typename Body>
void parallel_for_each(Iterator first, Iterator last, const Body& body);
```

例子如下：
```cpp
tbb::parallel_for_each(a.begin(), a.end(), [&] (float &f) 
{
    f = 32.f;
});
```
前两个参数接受迭代器区间，lambada表达式的参数f是输出参数，这个参数的类型取决于具体的问题。

### 4、二维范围版本
可以应用在图像处理上，函数声明和1基于区间的版本一样。
例子程序如下：
```cpp
tbb::parallel_for(tbb::blocked_range2d<size_t>(0, n, 0, n),
[&] (tbb::blocked_range2d<size_t> r) 
{
    for (size_t i = r.rows().begin(); i < r.rows().end(); i++) 
    {
        for (size_t j = r.cols().begin(); j < r.cols().end(); j++) 
        {
            a[i * n + j] = std::sin(i) * std::sin(j);
        }
    }
});
```


## 二、并行reduce
基本思想是将整个任务划分若干的组。
函数声明如下：
```cpp
template<typename Range, typename Value, typename RealBody, typename Reduction>
Value parallel_reduce( const Range& range, const Value& identity, const RealBody& real_body, const Reduction& reduction);
```

参数说明<br >range：范围
identity：初始值，例如求和的话可以设置为0
real_body：实际的函数体
reduction：规约操作

例子如下：
```cpp
size_t n = 1<<26;
float res = tbb::parallel_reduce(tbb::blocked_range<size_t>(0, n), (float)0,
[&] (tbb::blocked_range<size_t> r, float local_res) 
{
    for (size_t i = r.begin(); i < r.end(); i++) 
    {
        local_res += std::sin(i);
    }
    return local_res;
}, 
[] (float x, float y) 
{
    return x + y;
});
```

确定性结果的reduce

```cpp
template<typename Range, typename Value, typename RealBody, typename Reduction>
Value parallel_deterministic_reduce( const Range& range, const Value& identity, const RealBody& real_body, const Reduction& reduction);
```
并行缩并的额外好处：能避免浮点误差，例如求平均值。


## 三、性能测试
1、测试方法
测试所花费时间：tbb::tick_count::now()

例子程序如下，先计算数组中的每一项，然后进行规约求和
```cpp
#include <iostream>
#include <tbb/blocked_range.h>
#include <tbb/parallel_reduce.h>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    std::vector<float> a(n);

    TICK(for);
    // fill a with sin(i)
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r)
    {
        for (size_t i = r.begin(); i < r.end(); i++) {
            a[i] = std::sin(i);
        }
    });
    TOCK(for);

    TICK(reduce);
    // calculate sum of a
    float res = tbb::parallel_reduce(tbb::blocked_range<size_t>(0, n), (float)0,
    [&] (tbb::blocked_range<size_t> r, float local_res) {
        for (size_t i = r.begin(); i < r.end(); i++) {
            local_res += a[i];
        }
        return local_res;
    }, [] (float x, float y) {
        return x + y;
    });
    TOCK(reduce);

    std::cout << res << std::endl;

    TICK(for1);
    // fill a with sin(i)
    for (size_t i = 0; i < n; i++)
    {
        a[i] = std::sin(i);
    }
    TOCK(for1);

    res = 0.0;

    TICK(reduce1);
    // fill a with sin(i)
    for (size_t i = 0; i < n; i++)
    {
        res += a[i];
    }
    TOCK(reduce1);

    std::cout << res << std::endl;

    return 0;
}
```

测试结果如下：
并行：
for: 0.332907s
reduce: 0.0193183s
0.706159
串行
for1: 1.85208s
reduce1: 0.130157s
0.705693

测试的电脑是8代i7，6核12线程。从测试结果看，并行赋值操作加速比接近6，reduce的加速比超过6。

## 四、任务域与嵌套
1、任务域
使用tbb::task_arena作为一个任务域，可以指定并行的线程数量，例子如下：
```cpp
tbb::task_arena ta(4);
ta.execute([&]
{
    tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i)
    {
        a[i] = std::sin(i);
    });
});
```

2、for循环嵌套
例子
```cpp
tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i)
{
    tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t j)
    {
        a[i * n + j] = std::sin(i) * std::sin(j);
    });
});
```

但是，嵌套for循环可能会造成死锁问题，例如下面的代码
```cpp
tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i) {
    std::lock_guard lck(mtx);
    tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t j) {
        a[i * n + j] = std::sin(i) * std::sin(j);
    });
});
```
死锁原因：
因为TBB用了工作窃取法来分配任务：当一个线程t1做完自己队列里全部的工作时，会从另一个工作中线程t2的队列里取出任务，以免t1闲置浪费时间。
因此内部for循环有可能“窃取”到另一个外部for循环的任务，从而导致mutex被重复上锁。

解决办法
解决1：用标准库的递归锁 std::recursive_mutex
解决2：创建另一个任务域，这样不同域之间就不会窃取工作
解决3：同一个任务域，但用 isolate 隔离，禁止其内部的工作被窃取（推荐），具体代码如下：
```cpp
tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i) 
{
    std::lock_guard lck(mtx);
    tbb::this_task_arena::isolate([&] 
    {
        tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t j) 
        {
            a[i * n + j] = std::sin(i) * std::sin(j);
        });
    });
});
```

## 五、任务调度
### 1、任务划分策略

并行：如何均匀分配任务到每个线程？

解决1：线程数量超过CPU核心数量，让系统调度保证各个核心始终饱和
解决2: 线程数量不变，但是用一个队列分发和认领任务
解决3: 每个线程一个任务队列，做完本职工作后可以认领其他线程的任务，这个也叫做任务窃取法

### 2、tbb任务划分机制

#### （1）静态均匀划分static_partitioner
这种策略是将任务均匀的划分到不同的线程，对于每个任务计算复杂度一样的任务效果很好。例子代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include <thread>
#include "ticktock.h"
#include "mtprint.h"

int main() {
    size_t n = 32;

    tbb::task_arena ta(4);
    ta.execute([&]
    {
        tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
        [&] (tbb::blocked_range<size_t> r)
        {
            mtprint("thread", tbb::this_task_arena::current_thread_index(), "size", r.size());
            std::this_thread::sleep_for(std::chrono::milliseconds(400));
        }, tbb::static_partitioner{});
    });

    return 0;
}
```
执行结果如下：
thread 0 size 8
thread 1 size 8
thread 2 size 8
thread 3 size 8
创建了4个线程4个任务，每个任务包含8个元素。

另外可以指定区间的粒度，将tbb::parallel_for(tbb::blocked_range<size_t>(0, n)改为tbb::parallel_for(tbb::blocked_range<size_t>(0, n, 16)，执行的结果如下：
thread 0 size 16
thread 1 size 16
创建了2个线程2个任务，每个任务包含16个元素。

#### （2）、简单划分策略simple_partitioner
例子如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include <thread>
#include "ticktock.h"
#include "mtprint.h"

int main() {
    size_t n = 32;

    TICK(for);
    tbb::task_arena ta(4);
    ta.execute([&] {
        tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
        [&] (tbb::blocked_range<size_t> r)
        {
            for (size_t i = r.begin(); i < r.end(); i++)
            {
                mtprint("thread", tbb::this_task_arena::current_thread_index(),
                        "size", r.size(), "begin", r.begin());
                std::this_thread::sleep_for(std::chrono::milliseconds(i * 10));
            }
        }, tbb::simple_partitioner{});
    });
    TOCK(for);

    return 0;
}
```

执行结果如下：
thread 0 size 1 begin 0
thread 0 size 1 begin 1
thread 1 size 1 begin 16
thread 2 size 1 begin 8
thread 3 size 1 begin 12
thread 0 size 1 begin 2
thread 0 size 1 begin 3
thread 0 size 1 begin 4
thread 2 size 1 begin 9
thread 0 size 1 begin 5
thread 3 size 1 begin 13
thread 0 size 1 begin 6
thread 1 size 1 begin 17
thread 2 size 1 begin 10
thread 0 size 1 begin 7
thread 3 size 1 begin 14
thread 2 size 1 begin 11
thread 0 size 1 begin 15
thread 1 size 1 begin 18
thread 2 size 1 begin 24
thread 3 size 1 begin 20
thread 0 size 1 begin 22
thread 1 size 1 begin 19
thread 3 size 1 begin 21
thread 2 size 1 begin 25
thread 0 size 1 begin 23
thread 1 size 1 begin 28
thread 3 size 1 begin 26
thread 2 size 1 begin 30
thread 0 size 1 begin 29
thread 1 size 1 begin 31
thread 3 size 1 begin 27

创建了 4 个线程 32 个任务，每个任务包含 1 个元素

另外，也可以指定区间的粒度大小，将tbb::parallel_for(tbb::blocked_range<size_t>(0, n)改为tbb::parallel_for(tbb::blocked_range<size_t>(0, n, 4)

创建了 4 个线程 8 个任务，每个任务包含 4 个元素

#### （3）自动划分机制 auto_partitioner

根据lambada的执行时间，自动选择合适的划分策略。也是没有指定划分策略时的默认策略。

#### （4）根据历史经验自动负载均衡策略 affinity_partitioner
根据程序的历史执行时间，进行划分，重复运行同样的实例，时间会越来越少。

总结，需要根据具体问题的特性来选择，并且要多实验。例如简单话费配合合适的跨距会比自动划分的性能要高很多。


## 六、并发容器

并发容器主要是对标stl的容器，主要有vector/list/map/set等。
不连续的 tbb::concurrent_vector
std::vector 造成指针失效的根本原因在于他必须保证内存是连续的，从而不得不在扩容时移动元素。
因此可以用 tbb::concurrent_vector，他不保证元素在内存中是连续的。换来的优点是 push_back 进去的元素，扩容时不需要移动位置，从而指针和迭代器不会失效。
同时他的 push_back 会额外返回一个迭代器（iterator），指向刚刚插入的对象。

push_back 一次只能推入一个元素。
而 grow_by(n) 则可以一次扩充 n 个元素。他同样是返回一个迭代器（iterator），之后可以通过迭代器的 ++ 运算符依次访问连续的 n 个元素，* 运算符访问当前指向的元素。

除了内存不连续、指针和迭代器不失效的特点，tbb::concurrent_vector 还是一个多线程安全的容器，能够被多个线程同时并发地 grow_by 或 push_back 而不出错。
而 std::vector 只有只读的 .size() 和 [] 运算符是安全的，且不能和写入的 push_back 等一起用，否则需要用读写锁保护。

因为 tbb::concurrent_vector 内存不连续的特点，通过索引访问，比通过迭代器访问的效率低一些。
因此不推荐像a[i]这样通过索引随机访问其中的元素，*(it + i)这样需要迭代器跨步访问的也不推荐。

最好的方式是用begin()和end()的迭代器区间，按顺序访问。

## 七、并行筛选
例如小彭老师的课件中的筛选出sinx大于0的值的例子，列举出几种方案并对比不同方案

### 1、基础的串行版本
代码如下：

```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    std::vector<float> a;

    TICK(filter);
    for (size_t i = 0; i < n; i++) {
        float val = std::sin(i);
        if (val > 0) {
            a.push_back(val);
        }
    }
    TOCK(filter);

    return 0;
}
```

耗时：2.28205s

### 2、并行筛选版本1
利用多线程安全的 concurrent_vector 动态追加数据，在我的电脑上测试，性能还退化了，可能的原因是对同一个容器进行加锁和解锁，浪费了一定的时间。
加速比：0.9倍
代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <tbb/concurrent_vector.h>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    tbb::concurrent_vector<float> a;

    TICK(filter);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                a.push_back(val);
            }
        }
    });
    TOCK(filter);

    return 0;
}
```

耗时：2.51004s

### 3、并行筛选版本2
先推到线程局部（thread-local）的 vector，最后一次性推入到concurrent_vector
可以避免频繁在concurrent_vector上产生锁竞争
加速比：4.97倍
代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <tbb/concurrent_vector.h>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    tbb::concurrent_vector<float> a;

    TICK(filter);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        auto it = a.grow_by(local_a.size());
        for (size_t i = 0; i < local_a.size(); i++) {
            *it++ = local_a[i];
        }
    });
    TOCK(filter);

    return 0;
}
```
耗时：0.459141s

### 4、并行筛选版本3
线程局部的vector调用reserve预先分配一定内存，避免push_back反复扩容时的分段式增长
同时利用标准库的std::copy模板简化了代码。
加速比：5.31倍

代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <tbb/concurrent_vector.h>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    tbb::concurrent_vector<float> a;

    TICK(filter);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        local_a.reserve(r.size());
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        auto it = a.grow_by(local_a.size());
        std::copy(local_a.begin(), local_a.end(), it);
    });
    TOCK(filter);

    return 0;
}
```

耗时：0.429808s

### 5、并行筛选版本4
如果需要筛选后的数据是连续的，即a是个 std::vector，这时就需要用mutex锁定，避免数据竞争。
加速比：3.46倍

代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include <mutex>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    std::vector<float> a;
    std::mutex mtx;

    TICK(filter);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        local_a.reserve(r.size());
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        std::lock_guard lck(mtx);
        std::copy(local_a.begin(), local_a.end(), std::back_inserter(a));
    });
    TOCK(filter);

    return 0;
}
```

耗时：0.660342s

### 6、并行筛选版本5
在版本4的基础上，先对a预留一定的内存，避免频繁扩容影响性能。
加速比：4.51倍

代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include <mutex>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    std::vector<float> a;
    std::mutex mtx;

    TICK(filter);
    a.reserve(n * 2 / 3);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        local_a.reserve(r.size());
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        std::lock_guard lck(mtx);
        std::copy(local_a.begin(), local_a.end(), std::back_inserter(a));
    });
    TOCK(filter);

    return 0;
}
```

耗时：0.506221s

### 7、并行筛选版本6
在版本6的基础上，修改std互斥锁为tbb的自旋锁。加速比：3.44倍。
代码如下：
```cpp
#include <iostream>
#include <tbb/parallel_for.h>
#include <tbb/spin_mutex.h>
#include <vector>
#include <cmath>
#include <mutex>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    std::vector<float> a;
    tbb::spin_mutex mtx;

    TICK(filter);
    a.reserve(n * 2 / 3);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        local_a.reserve(r.size());
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        std::lock_guard lck(mtx);
        std::copy(local_a.begin(), local_a.end(), std::back_inserter(a));
    });
    TOCK(filter);

    return 0;
}
```

耗时：0.661881s

从以上方案可以看出，最能满足实际需求的是版本5，小彭老师也是推荐用这种方案。

## 八、并行排序
tbb提供了tbb::parallel_sort供我们进行并行的排序。下面就根据小彭老师提供的测试代码
来实际验证下tbb::parallel_sort对比std::sort的加速效果。

1、串行基准程序
```cpp
#include <iostream>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <algorithm>
#include "ticktock.h"

int main() {
    size_t n = 1<<24;
    std::vector<int> arr(n);
    std::generate(arr.begin(), arr.end(), std::rand);
    TICK(std_sort);
    std::sort(arr.begin(), arr.end(), std::less<int>{});
    TOCK(std_sort);
    return 0;
}
```

耗时：1.21626s

2、并行排序
```cpp
#include <iostream>
#include <cstdlib>
#include <vector>
#include <cmath>
#include <algorithm>
#include <tbb/parallel_sort.h>
#include "ticktock.h"

int main() {
    size_t n = 1<<24;
    std::vector<int> arr(n);
    std::generate(arr.begin(), arr.end(), std::rand);
    TICK(tbb_parallel_sort);
    tbb::parallel_sort(arr.begin(), arr.end(), std::less<int>{});
    TOCK(tbb_parallel_sort);
    return 0;
}
```

耗时：0.269297s

可以计算出，并行加速比为4.52倍，加速效果还是不错的。

最后，tbb还有很多功能等待挖掘，真正发挥它的作用，可以在工作中多多使用它。