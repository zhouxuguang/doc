# Vulkan的VK_KHR_dynamic_rendering使用方法

## 一、简介
    vulkan1.0的时候，想必大家都被VkRenderPass和VkFrameBuffer所困惑，1.0版本中
    使用一个pass需要创建一个VkRenderPass，然后也需要创建VkFrameBuffer，VkFrameBuffer同时又依赖VkRenderPass，最后pipeline对象又依赖VkRenderPass，这样就导致关系错综复杂。
其实按照我的理解，当开始一个renderpass的时候，主要的信息就是对所谓的rendertarget进行设置，rendertarget主要包括有几个颜色通道的目标，
以及深度模板的目标纹理是哪个；当然也包括他们各自的格式以及load、store操作的方式。
    vulkan最近推出了VK_KHR_dynamic_rendering，旨在简化renderpass的流程，完全可以去掉VkRenderPass和VkFrameBuffer这两个对象的创建，
这个扩展在1.3版本中也提升为了核心规范。大家想要使用这个扩展，可以使用最新的驱动和vulkan SDK。那现在话不多说，来看看怎么开启这个扩展，以及怎么使用它。

## 二、使用方法
### 1、检查扩展
检查设备的扩展列表，这个很简单。
```cpp
enabledDynamicRendering = ExtensionSupported(VK_KHR_DYNAMIC_RENDERING_EXTENSION_NAME);
```

### 2、开启创建VkDevice的扩展
在创建设备对象时，开启对应的扩展，代码也很简单
```cpp
if (context.vulkanExtension.enabledDynamicRendering)
{
    deviceExtensionNames.push_back(VK_KHR_DYNAMIC_RENDERING_EXTENSION_NAME);
}
```

另外需要指定VkPhysicalDeviceDynamicRenderingFeaturesKHR 结构体，然后deviceCreateInfo中的pNext字段指向这个结构体，具体代码如下：
```cpp
const VkPhysicalDeviceDynamicRenderingFeaturesKHR dynamicRenderingFeature
{
    .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DYNAMIC_RENDERING_FEATURES_KHR,
    .pNext = nullptr,
    .dynamicRendering = VK_TRUE,
};
deviceQueueCreateInfo->pNext = &dynamicRenderingFeature;
```
需要注意的是dynamicRendering字段必须指定为VK_TRUE。

### 3、 renderpass阶段
开始阶段使用vkCmdBeginRenderingKHR这个函数，注意这个函数指针的加载可以使用vol
自动加载或者自己手动加载。该函数接受两个参数，第一个参数是commandBuffer，另一个
参数是VkRenderingInfo，这个结构体定义如下：
```cpp
typedef struct VkRenderingInfo {
    VkStructureType                     sType;
    const void*                         pNext;
    VkRenderingFlags                    flags;
    VkRect2D                            renderArea;
    uint32_t                            layerCount;
    uint32_t                            viewMask;
    uint32_t                            colorAttachmentCount;
    const VkRenderingAttachmentInfo*    pColorAttachments;
    const VkRenderingAttachmentInfo*    pDepthAttachment;
    const VkRenderingAttachmentInfo*    pStencilAttachment;
} VkRenderingInfo;
```
另外VkRenderingAttachmentInfo结构体就可以指定各个Attachment的信息，主要包括imageview、load、store操作等必要的信息。其结构体定义如下：
```cpp
typedef struct VkRenderingAttachmentInfo {
    VkStructureType          sType;
    const void*              pNext;
    VkImageView              imageView;
    VkImageLayout            imageLayout;
    VkResolveModeFlagBits    resolveMode;
    VkImageView              resolveImageView;
    VkImageLayout            resolveImageLayout;
    VkAttachmentLoadOp       loadOp;
    VkAttachmentStoreOp      storeOp;
    VkClearValue             clearValue;
} VkRenderingAttachmentInfo;
```

结束阶段就比较简单，直接调用vkCmdEndRenderingKHR(mCommandBuffer);就可以了。

还有一点需要说明的是，在renderpass开始之前，以及结束之后，需要对关联的图像进行布局的转换。
```cpp
// 动态渲染没有子流程依赖，所以需要插入图像内存屏障，pass开始之前
for (auto &iter : mPassImage.colorImages)
{
    VulkanBufferUtil::InsertImageMemoryBarrier(
                                                mCommandBuffer,
                                                iter,
        0,
        VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
        VK_IMAGE_LAYOUT_UNDEFINED,
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
        VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
        VkImageSubresourceRange{ VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 });
}

//pass结束之后
// 对颜色附件进行转换
for (auto &iter : mPassImage.colorImages)
{
    VulkanBufferUtil::InsertImageMemoryBarrier(
                                            mCommandBuffer,
                                                iter,
        VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT,
        0,
        VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
                                                imageLayout,
        VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
        VK_PIPELINE_STAGE_BOTTOM_OF_PIPE_BIT,
        VkImageSubresourceRange{ VK_IMAGE_ASPECT_COLOR_BIT, 0, 1, 0, 1 });
}
```

这个布局转换各位根据自己的实际情况进行调整，另外代码片段中是截取个人自研引擎中的代码片段，有一些上下文缺失，不过基本的意思应该是表达清楚了。

### 4、创建管线的结构体设置
除了以上几点，创建管线的时候需要指定各个Attachment的格式信息，其实这个也和Metal是类
似的。其代码如下：
```cpp
std::vector<VkPipelineRenderingCreateInfoKHR> renderingCreateInfos;
if (mContext->vulkanExtension.enabledDynamicRendering)
{
    // New create info to define color, depth and stencil attachments at pipeline create time
    VkPipelineRenderingCreateInfoKHR pipelineRenderingCreateInfo = {};
    pipelineRenderingCreateInfo.sType = VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO_KHR;
    pipelineRenderingCreateInfo.colorAttachmentCount = (uint32_t)passFormat.colorFormats.size();
    pipelineRenderingCreateInfo.pColorAttachmentFormats = passFormat.colorFormats.data();
    pipelineRenderingCreateInfo.depthAttachmentFormat = passFormat.depthFormat;
    pipelineRenderingCreateInfo.stencilAttachmentFormat = passFormat.stencilFormat;
    renderingCreateInfos.push_back(pipelineRenderingCreateInfo);
    
    // 动态渲染需要把renderpass设置为空
    mPipeCreateInfo.renderPass = nullptr;
}
mPipeCreateInfo.pNext = renderingCreateInfos.data();
```

代码中的passFormat也是个人引擎中的东西，各位换为自己的格式就好。

## 三 总结
由于本人的电脑是mac，所以实际使用的vulkan驱动是MoltenVK，最终是调用系统的Metal驱动
来实现，这个renderpass就对应到Metal的MTLRenderCommandEncoder对象。


