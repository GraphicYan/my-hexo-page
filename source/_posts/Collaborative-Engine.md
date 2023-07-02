---
title: 浅谈端云协同渲染
layout: Collaborative Rendering and Engine
toc: true
date: 2023/02/21 12:33:15
---

## 原创性声明
本文为作者原创，在个人Blog首次发布，如需转载请注明引用出处。（yanzhang.cg@gmail.com 或 https://graphicyan.github.io/）


<a name="KVfi6"></a>
### 从云游戏到混合渲染
<a name="sCIFE"></a>
#### 云游戏（Cloud Game）
<a name="CVocR"></a>
##### 原理

- 发送用户输入，从端到云。
- 渲染完整帧，云。
- 将画面以视频流传回，从云到端。
<a name="aL2co"></a>
##### 特点

- 适用于异构、低级别的终端设备。
- 围绕高效的视频压缩及传输技术构造技术生态。
- 延迟（~100ms），视频类应用尚可接受、交互式对抗类游戏会难以忍受。
- 传输带宽限制，对压缩算法的挑战。
<a name="nlhm9"></a>
#### 混合渲染（Hybrid Rendering）
<a name="MI7jy"></a>
##### 原理

- 端侧以实时计算的Raster及ComputeShader为主，保证基本的输出。
- 辅以云侧的Raytrace、GI、AO、Translucency等算法，增强端侧效果。
<a name="wLYhi"></a>
##### 特点

- 算力适合地分布在云、端侧，协同两侧资源计算，混合计算结果。
- 策略丰富、增强效果、传输数据具有定制化（可优化空间）。
- 数据量相比云游戏方案，一般来说更小。
- 技术选型风险、工业化程度低。
<a name="TItIC"></a>
### 云游戏
把算力放在云端，看似简单，想要在端侧、云侧通信并实时处理逻辑、用户输入、渲染、捕获、编码、打包、传输、解码、显示，仍然由诸多难点和不确定性。
<a name="ZdPFh"></a>
#### Framework for Cloud Gaming
![image.png](assets/post_images/Collaborative-Engine/image_001.png#clientId=u602bfa2e-1565-4&from=paste&height=635&id=u64eb5e77&originHeight=889&originWidth=1406&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=482148&status=done&style=none&taskId=u5e13ed22-eabe-4e7a-ae85-0cf48979b3e&title=&width=1004.2857313885984)<br />![image.png](assets/post_images/Collaborative-Engine/image_002.png#clientId=u602bfa2e-1565-4&from=paste&height=460&id=u02077730&originHeight=664&originWidth=719&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=167659&status=done&style=none&taskId=ub7c33325-5996-4722-bd1b-d9f65dfd621&title=&width=498)<br />![image.png](assets/post_images/Collaborative-Engine/image_003.png#clientId=u602bfa2e-1565-4&from=paste&height=485&id=u2fcaef81&originHeight=799&originWidth=823&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=234901&status=done&style=none&taskId=u1a2a19a8-04c2-4971-aa66-824ba165837&title=&width=500)
<a name="DqIco"></a>
##### 延迟
![image.png](assets/post_images/Collaborative-Engine/image_004.png#clientId=u602bfa2e-1565-4&from=paste&height=163&id=u3abfb9e2&originHeight=399&originWidth=1222&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=203056&status=done&style=none&taskId=u7235202c-3547-4df5-aadf-3440b5cffd8&title=&width=500)
<a name="DOqdj"></a>
#### 技术分类
<a name="xFEab"></a>
##### 平台技术

- **系统集成**：组建云游戏（计算）的基础平台。
- **服务质量分析（QoS）：**主要集中在两种指标，**能量开销（**电池**）** 和 **网络指标（**延迟**）。**
- **体验质量分析（QoE）：**用户的主观评分，本质上乏味且贵，大多数尝试分析QoS和QoE的关系来反推QoE。
<a name="lwW46"></a>
##### 平台优化

- **云服务器基建：**多数据中心、服务节点、客户端的**资源分配**问题；如P2P覆盖及多层云等**分布式架构**。
- **通信：**如多层编码和图形压缩等**数据压缩**方法；**自适应传输**根据网络动态适时更改编码比特率、帧率、分辨率等参数。

<a name="xSV1b"></a>
#### 实现示例
<a name="CWcPw"></a>
##### 平台部署
![](assets/post_images/Collaborative-Engine/image_005.png?x-oss-process=image%2Fresize%2Cw_848%2Climit_0#from=url&id=XEUvw&originHeight=1150&originWidth=848&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&status=done&style=none&title=)
<a name="aT4m6"></a>
##### WebRTC
一个成熟的实时通信架构，应该具备音视频传输、多平台支持、插件管理等功能。<br />![成熟的实时通信具备的能力](assets/post_images/Collaborative-Engine/image_006.jpeg?x-oss-process=image%2Fresize%2Cw_1049%2Climit_0%2Finterlace%2C1#from=url&id=XzYD9&originHeight=722&originWidth=1049&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=true&status=done&style=none&title=%E6%88%90%E7%86%9F%E7%9A%84%E5%AE%9E%E6%97%B6%E9%80%9A%E4%BF%A1%E5%85%B7%E5%A4%87%E7%9A%84%E8%83%BD%E5%8A%9B "成熟的实时通信具备的能力")<br />WebRTC实现了上面所有的功能，是做网络实时通信的最优解。<br />目前UE的云游戏、淘宝直播、以及ZOOM等都用这套方案。<br />![webrtc架构图](assets/post_images/Collaborative-Engine/image_007.jpeg?x-oss-process=image%2Fresize%2Cw_1049%2Climit_0%2Finterlace%2C1#from=url&id=YfsGs&originHeight=982&originWidth=1049&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=true&status=done&style=none&title=webrtc%E6%9E%B6%E6%9E%84%E5%9B%BE "webrtc架构图")<br />![VS自研](assets/post_images/Collaborative-Engine/image_008.jpeg#from=url&id=Od2sY&originHeight=422&originWidth=1104&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=true&status=done&style=none&title=VS%E8%87%AA%E7%A0%94 "VS自研")
<a name="e8TPM"></a>
###### 使用WebRTC实现云推流
![](assets/post_images/Collaborative-Engine/image_009.png?x-oss-process=image%2Fresize%2Cw_1049%2Climit_0#from=url&id=egyIn&originHeight=403&originWidth=1049&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&status=done&style=none&title=)

1. 云端引擎的像素流送模块首先将建立到信令和Web服务器的链接。
2. 客户端会连接到信令服务器，服务器将对客户端提供一个HTML页面，其中包含播放器控件和以JavaScript编写的控制代码。
3. 用户开始流送时，信令服务器将进行交涉，在客户端浏览器和云端引擎之间建立直接连接。客户端和云端引擎须了解相互的IP地址，此连接方能工作。如两者在同一网络中运行，通常它们可看到各自的IP地址。然而在两个端点之间运行的网络地址转换（NAT）服务可能对任意一方的外部可见IP地址进行修改。解决此问题的方法通常是是用STUN或TURN服务器，告知每个组件其自身的外部可见IP地址。
4. 客户端和云侧引擎之间的连接建立后，像素流送模块便会直接开始将媒体流送到浏览器。来自客户端的输入由播放器页面的JavaScript环境直接发送回云端引擎中。
5. 即使媒体流送已经开始播放，信令和Web服务器仍会维持其与浏览器和云端引擎的连接，以便在必要时将用户从流送中移除，并处理浏览器造成的连接断开。

<a name="EgMGc"></a>
### 混合渲染 
<a name="AgiXu"></a>
#### 基于差异的协同渲染
<a name="F8Blq"></a>
##### Delta Encoding
![Delta Encoding](assets/post_images/Collaborative-Engine/image_010.png#clientId=u6c985579-b31a-4&from=paste&height=346&id=u9e79b35d&originHeight=484&originWidth=1096&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=true&size=134356&status=done&style=none&taskId=u740a3788-e34f-495c-a72c-4573e4a61f4&title=Delta%20Encoding&width=782.8571561891208 "Delta Encoding")<br />![image.png](assets/post_images/Collaborative-Engine/image_011.png#clientId=u6c985579-b31a-4&from=paste&height=615&id=udc6bbd07&originHeight=879&originWidth=908&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=1154804&status=done&style=none&taskId=u7244bc89-0a0c-45e9-bea7-99a0fcb2476&title=&width=635)<br />![image.png](assets/post_images/Collaborative-Engine/image_012.png#clientId=u6c985579-b31a-4&from=paste&height=307&id=u27583dfc&originHeight=430&originWidth=861&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=613435&status=done&style=none&taskId=u5433f83a-3bbf-45e1-bcb9-50d1267acf5&title=&width=615.0000104733878)
<a name="vQree"></a>
##### I-Frame Rendering
![Client-Side I-Frame Rendering](assets/post_images/Collaborative-Engine/image_013.png#clientId=u6c985579-b31a-4&from=paste&height=321&id=u20f03a62&originHeight=450&originWidth=1121&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=true&size=122778&status=done&style=none&taskId=ua047e6cc-ce19-426a-9625-180863a1525&title=Client-Side%20I-Frame%20Rendering&width=800.714299350369 "Client-Side I-Frame Rendering")
<a name="fRD3Y"></a>
#### 云光线追踪
![image.png](assets/post_images/Collaborative-Engine/image_014.png#clientId=u6c985579-b31a-4&from=paste&height=55&id=u89247432&originHeight=77&originWidth=348&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=15287&status=done&style=none&taskId=ua4b558d6-b380-4c1f-93f5-271383ab0f7&title=&width=248.57143280457484)<br />![image.png](assets/post_images/Collaborative-Engine/image_015.png#clientId=u6c985579-b31a-4&from=paste&height=1301&id=uad26227d&originHeight=1821&originWidth=2085&originalType=binary&ratio=1.399999976158142&rotation=0&showTitle=false&size=1773956&status=done&style=none&taskId=u4a4eac5d-7d87-4ff0-8213-1cfe234793a&title=&width=1489.2857396480993)
<a name="u71fy"></a>
#### 分布式动态光照探针
![[A Distributed, Decoupled System for Losslessly
 Streaming Dynamic Light Probes to Thin Clients]](assets/post_images/Collaborative-Engine/image_016.png#clientId=u31aa8cf2-a761-4&from=paste&height=306&id=u232887b9&originHeight=589&originWidth=1576&originalType=binary&ratio=1.9250000715255737&rotation=0&showTitle=true&size=434252&status=done&style=none&taskId=u1af1f252-7bd9-4f98-931a-8a271c769e9&title=%5BA%20Distributed%2C%20Decoupled%20System%20for%20Losslessly%0D%20Streaming%20Dynamic%20Light%20Probes%20to%20Thin%20Clients%5D&width=818.701268281518 "[A Distributed, Decoupled System for Losslessly
 Streaming Dynamic Light Probes to Thin Clients]")
<a name="WOjXr"></a>
#### 开个脑洞
<a name="Hs2vd"></a>
##### NV's Hybrid Pipeline
![[Hybrid Rendering for Real-Time Ray Tracing]](assets/post_images/Collaborative-Engine/image_017.png#clientId=u31aa8cf2-a761-4&from=paste&height=1122&id=XEiVy&originHeight=2160&originWidth=3840&originalType=binary&ratio=1.9250000715255737&rotation=0&showTitle=true&size=5925382&status=done&style=none&taskId=u7e7d609a-aaef-4273-81a3-27a599f15d5&title=%5BHybrid%20Rendering%20for%20Real-Time%20Ray%20Tracing%5D&width=1995 "[Hybrid Rendering for Real-Time Ray Tracing]")

<a name="P5kHz"></a>
## 参考文献
[2020][VR]Cloud-to-end Rendering and Storage Management for Virtual Reality in Experimental Education

[2022][IXR]Distributed Hybrid Rendering for Metaverse Experiences

[2022][PG Poster]Cloud-Assisted Hybrid Rendering for Thin-Client Games and VR Applications

[2022]A Full Dive into Realizing the Edge-enabled Metaverse

[2008][ICIP]Low Delay Streaming of Computer Graphics

[2009]Geelix_LiveGames_Remote_Playing_of_Video_Games

[2015][MobiSys]Kahawai

[2016]Mobile Cloud Computing Research

[2020][MICRO]A Benchmarking Framework for Interactive 3D Applications in the Cloud

[2020][MTA]A Hybrid Remote Rendering Method for Mobile

[GitHub - EpicGames/PixelStreamingInfrastructure: The official Pixel Streaming servers and frontend.](https://github.com/EpicGames/PixelStreamingInfrastructure)<br />

[Build software better, together](https://github.com/EpicGames/UnrealEngine/tree/release/Engine/Plugins/Media/PixelStreaming)<br />

[Real-time Streaming Of 3D Enterprise Applications From The Cloud To Low-powered Devices - CSE Developer Blog](https://devblogs.microsoft.com/cse/2019/03/19/real-time-streaming-of-3d-enterprise-applications-from-the-cloud-to-low-powered-devices/)<br />

[Unreal Pixel Streaming in Azure - Azure Gaming](https://learn.microsoft.com/en-us/gaming/azure/reference-architectures/unreal-pixel-streaming-in-azure)<br />

[像素流介绍](https://docs.unrealengine.com/5.1/zh-CN/overview-of-pixel-streaming-in-unreal-engine/)<br />

[搞懂WebRTC ，看这一篇就够了](https://zhuanlan.zhihu.com/p/580146138)<br />

[WebRTC和WebSocket有什么关系和区别？ - 知乎](https://www.zhihu.com/question/424264607/answer/2394172608)<br />

[音视频通信为什么要选择WebRTC？](https://zhuanlan.zhihu.com/p/409462524)<br />

[【技术】UE4 Pixel Streaming 详细解读（实践篇）](https://zhuanlan.zhihu.com/p/63093901)<br />

[PixelStreaming 局域网及公有云部署全流程记录](https://zhuanlan.zhihu.com/p/153098799)<br />

[UE4像素流（Pixel Streaming）应用场景](https://zhuanlan.zhihu.com/p/76406905)
