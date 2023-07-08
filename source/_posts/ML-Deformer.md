---
title: 基于机器学习的物理变形器
layout: Machine Learning Deformer
toc: true
date: 2023/07/08 10:45:15
---

## 原创性声明
本文为作者原创，在个人Blog首次发布，如需转载请注明引用出处。（yanzhang.cg@gmail.com 或 https://graphicyan.github.io/）


![63438006e420c.gif](assets/post_images/ML-Deformer/image_000.gif#clientId=u4bdc6d29-ffc6-4&from=ui&id=u89367ca0&originHeight=364&originWidth=600&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=1480303&status=done&style=none&taskId=u1e8cc65e-20fe-48b4-80e8-d04f0823af3&title=)<br />![6343800937219.gif](assets/post_images/ML-Deformer/image_001.gif#clientId=u4bdc6d29-ffc6-4&from=ui&id=u2061c80b&originHeight=364&originWidth=600&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=963967&status=done&style=none&taskId=u05d50c93-3dfb-477d-8a84-52655767d67&title=)
<a name="Ht3aT"></a>
### UE5中的应用示例
<a name="V2TZk"></a>
#### Workflow
![](assets/post_images/ML-Deformer/image_002.png#clientId=ue576d69d-1fe4-4&from=paste&id=u1fc8d6e3&originHeight=464&originWidth=1440&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u491e2ce0-0b64-4487-b029-1417e003465&title=)
<a name="kobZ1"></a>
#### ML Deformer in UE5
<a name="LDvdc"></a>
##### Vertex Delta Model

- 基于GPU的神经网络。
- 顶点差是参数。
- 性能较为糟糕。
<a name="hcNwh"></a>
##### Neural Morph Model（NMM）

- 神经形变模型，UE5的Morph Target的神经网络版。
- 基于CPU的神经网络。
- 适用于Muscle、Flesh对象的拟合。
- 需要针对特定对象进行二次训练，更新权重张量。（如：“火箭浣熊”与“星爵"的骨骼-肌肉动作明显不同）。
<a name="qwVjw"></a>
##### Nearest Neighbor Model（NNM）

- 最近邻模型。
- 适合布料对象的模拟。

<a name="dao12"></a>
#### Performance on PS5
![image.png](assets/post_images/ML-Deformer/image_003.png#clientId=u4bdc6d29-ffc6-4&from=paste&height=944&id=ud1bf370a&originHeight=1275&originWidth=1209&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=537245&status=done&style=none&taskId=uc85f8b83-a62f-485b-a0e5-dc83c8ed582&title=&width=895.5556188198809)
<a name="xR9fs"></a>
### 肌肉模拟
![image.png](assets/post_images/ML-Deformer/image_004.png#clientId=u6a4714c5-a100-4&from=paste&height=499&id=ue3f0bd87&originHeight=673&originWidth=1156&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=565062&status=done&style=none&taskId=u4824e172-1002-4ea6-9300-e21ef1ad3be&title=&width=856.2963567872476)
<a name="YPdde"></a>
#### 原理
![MLAsset4.gif](assets/post_images/ML-Deformer/image_005.gif#clientId=u4bdc6d29-ffc6-4&from=ui&id=u7222109f&originHeight=528&originWidth=744&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=9163271&status=done&style=none&taskId=u994a91b5-8948-407f-99be-1e9e5cd5dc2&title=)<br />![image.png](assets/post_images/ML-Deformer/image_006.png#clientId=u4bdc6d29-ffc6-4&from=paste&id=uc80db7e6&originHeight=969&originWidth=1871&originalType=url&ratio=1.3499999046325684&rotation=0&showTitle=false&size=505797&status=done&style=none&taskId=u7ce7d369-5fb0-48e3-89d4-ae3056cb865&title=)
<a name="IHClX"></a>
##### Local模式

- 由多个单独的小网络学习各关节周围的变形。
- 需要的数据集相对少。
- 每根骨骼都会创建一组变形目标，总的Morph Traget数为：

(num_bones + num_bone_groups) * num_morphs_per_bone_or_curve + (num_curves + num_curve_groups) * num_morphs_per_bone_or_curve + 1
<a name="x99kd"></a>
##### Global

- 整个网络是全连接的。
- 从所有相关关节的协调运动中学习变形。
- 需要的数据集和训练时间也相对更长。
- 网络实现与Local类似，且更简单一些。
<a name="jKe2m"></a>
#### 数据集

- 使用Maya中的PosGenTool插件。
- 官方推荐5000个随机pose，一般需要5000~15000个姿态。
- 在Maya或Houdini中，使用离线的变形器进行肌肉模拟（如Houdini中基于PBD的Vellum）。
- 输出肌肉文件（Alembic格式）通常比较大，几十~几百个G。
<a name="JMkNn"></a>
#### 限制

- 数据集生成、训练耗时。
- 不同角色有较强的的特适性。
<a name="BQ7Q9"></a>
### 布料模拟
![physics-mlcloth-2.gif](assets/post_images/ML-Deformer/image_007.gif#clientId=u6a4714c5-a100-4&from=ui&id=u28095488&originHeight=502&originWidth=888&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=36645300&status=done&style=none&taskId=u137207a1-6839-47ac-929e-5a9568243d0&title=)
<a name="r9zVS"></a>
#### 原理
![physics-mlcloth.gif](assets/post_images/ML-Deformer/image_008.gif#clientId=ub84dd715-4c16-4&from=ui&id=ufe1854b2&originHeight=402&originWidth=800&originalType=binary&ratio=1.5749999284744263&rotation=0&showTitle=false&size=11740088&status=done&style=none&taskId=ue32df4ed-345f-44f1-bab3-da0767fd324&title=)<br />两个阶段
<a name="b3KxA"></a>
##### 神经变形模型（ML Deformer）
**低频率变形**，使用多层感知机（MLP）建模，网络输出PCA系数。<br />pca_delta = mean_delta + pca_coeff * pca_basis<br />推荐采用5000个姿势。
<a name="IENTJ"></a>
##### 最近邻模型(Nerest Neighbor)
**高频率变形**，ML的变体，从上述获得PCA系数后，在“最近邻”数据集中搜索最接近的值。<br />vertex_delta = pca_delta + nearest_neighbor_delta<br />推荐采用50~100个姿势。<br />可以用KMeans Pose Generator来进行自动姿势选择。
<a name="vbw99"></a>
#### 数据集

- 待仿真结果稳定，Houdini Vellum。
- 关闭重力。
- ML Deformer使用尽可能随机的姿势，确保每个关节都充分采样了所有角度。
- ML Deformer尽量多一些姿势，建议5000个以上。
<a name="hQIJI"></a>
#### 限制

- 半静态服装，可预测褶皱，无法预测摇摆等动态移动。
- 适合紧身服装，不适合宽松。

<a name="L1dLQ"></a>
### 附：经典常用蒙皮方法
<a name="xC40j"></a>
#### 线性蒙皮（LBS）
![image.png](assets/post_images/ML-Deformer/image_009.png#clientId=u4bdc6d29-ffc6-4&from=paste&height=83&id=u69f89c35&originHeight=112&originWidth=580&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=26577&status=done&style=none&taskId=u9478678e-593e-496a-a7f0-79117cfcb1f&title=&width=429.6296599797609)
<a name="nAqGe"></a>
#### 线性对偶四元数蒙皮（DQS)
![image.png](assets/post_images/ML-Deformer/image_010.png#clientId=u4bdc6d29-ffc6-4&from=paste&height=82&id=u28103d5c&originHeight=111&originWidth=793&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=32827&status=done&style=none&taskId=u2aee5806-7d12-475c-b7d8-87360ce007d&title=&width=587.4074489033627)
<a name="PyBC8"></a>
#### 姿态空间变形（Pose Space Deformer）

- UE5中的Morph Target的Deformer Graph
- Houdini中的Niagara的GPU Simulation
- 非线性变形
- 需要TA干引擎的货，审美基础上开发特适的变形器：“晶格变形器，簇变形器，褶皱变形器，张力变形器，抖动变形器”等。
<a name="cOj8m"></a>
### 参考
[Nearest Neighbor Model | Tutorial](https://dev.epicgames.com/community/learning/tutorials/2lJy/unreal-engine-nearest-neighbor-model)<br />[机器学习布料模拟概述](https://docs.unrealengine.com/5.2/zh-CN/machine-learning-cloth-simulation-overview/)<br />[如何使用机器学习变形器](https://docs.unrealengine.com/5.2/zh-CN/how-to-use-the-machine-learning-deformer-in-unreal-engine/)<br />[UE5 机器学习变形器解析](https://zhuanlan.zhihu.com/p/632849525)
