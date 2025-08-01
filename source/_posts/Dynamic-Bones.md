---
title: 基于动力学的骨骼动画技术综述
layout: Physics-based Dynamic Bones
toc: true
top: true
tag: Animations
date: 2023/07/02 15:17:15
---

## 原创性声明
本文为作者原创，在个人Blog首次发布，如需转载请注明引用出处。（yanzhang.cg@gmail.com 或 https://graphicyan.github.io/）



<a name="qWnXp"></a>
## DynamicBone (Unity)
<a name="ghTlk"></a>
### INTRO
[Dynamic Bone | Animation Tools | Unity Asset Store](https://assetstore.unity.com/packages/tools/animation/dynamic-bone-16743)<br />![](assets/post_images/Dynamic-Bones/image_000.webp#clientId=u655dc2f2-1117-4&from=paste&id=u0435447e&originHeight=370&originWidth=605&originalType=url&ratio=1.2000000476837158&rotation=0&showTitle=false&status=done&style=none&taskId=u4838b198-897a-49ae-9043-d88a17deaa8&title=)<br />DynamicBone是一个简单的基于模拟弹簧振子的算法实现树状柔体的物理模拟插件。虽然基于模拟弹簧振子运动的算法实现，但是DynamicBone各节点之间的距离实际上不会发生变化。比起弹簧，父子节点之间的相对运动更接近串联的单摆。
<a name="Ak973"></a>
### 工作流
<a name="bM8vS"></a>
#### 基本操作
绑定Dynamic Bone，设置对应的Root、Colliders、及相关动力参数。<br />![image.png](assets/post_images/Dynamic-Bones/image_001.png#clientId=ucec9efd8-48da-4&from=paste&height=949&id=ude4f18a8&originHeight=1495&originWidth=1154&originalType=binary&ratio=1.5749999284744263&rotation=0&showTitle=false&size=452568&status=done&style=none&taskId=u3aa7ff6b-b222-4f80-b6f7-d60f0c97b97&title=&width=732.6984459724931)

<a name="ZYken"></a>
#### 属性参数

- **Damping （阻尼）：**阻止简谐运动的惯性运动，相当于弹簧的摩擦力。为0时简谐运动过程不会主动停止，为1时简谐运动过程不会发生。
- **Elasticity （弹性）：**决定回振移动强度，在简谐运动过程中作为额外的作用力将节点拉到还原位置，相当于弹簧的弹力。为0时系统形变不会主动还原，为1时形变不会发生。
- **Stiffness （刚性）：**限制最大振动幅度与方向，保证碰撞处理前节点不会跑到指定范围外，相当于弹簧的硬度。为0时不发挥作用，0到1时限制范围从2倍原始距离到0线性衰减。
- **Inert （惯性）：**限制形变幅度，在每一帧的简谐运动迭代发生前，无条件随物体整体运动拉动节点，拉动距离为Inert * 整体运动距离 。
- **Update （更新频率）：**DynamicBone计算频率，当游戏实际帧率高于这个更新频率时，DynamicBone会在每一帧进行消极计算，会尽量保持节点形状，但不会进行简谐运动模拟；当DynamicBone更新 频率远远高于游戏帧率的时候，DynamicBone会在脚本执行时尝试追帧，但每次最多执行4次，也就是更新频率实际最高只是当前游戏帧数的4倍。
- **Radius （半径）：**指定每个节点与DynamicBoneCollider发生碰撞的半径，注意节点互相之间不存在碰撞关系，这个半径是0碰撞依然会生效。
- **Damping\Elasticity\Stiffness\Inert\Radius各属性的Distrib：**指定属性随着节点深度递增发生的变化；
- **End Length\End Offset 末尾节点偏移量：**指定特殊的末尾节点End Bone局部位置。
- **Gravity 重力：**在DynamicBone节点上施加的重力，方向是在全局坐标系中的，注意DynamicBone的重力比较特殊，只在节点运动发生时起效，会在节点运动时把节点向重力方向拉动。
- **Force 常驻力：**在DynamicBone节点上施加的额外力，方向是在全局坐标系中的，注意Force与Gravity不同，是无条件生效的，会一直把节点向指定方向拉动。
- **Colliders 碰撞体列表：**会与DynamicBone各节点发生碰撞的碰撞体对象。
- **Exclusions 排除节点列表：**在设置Root节点后，DynamicBone会根据节点的GameObject的父子关系沿着子GameObject方向自动生成节点树，Exclusions中所有节点及其子孙节点都不会 生成DynamicBone节点。
- **Freeze Axis 固定轴：**非None的情况下，所有节点在局部坐标系的对应的轴上在值不会发生变化。
- **DistanceDisable 距离控制开关：**开启或者关闭距离控制机制，开启后如果DynamicBone所在的物体超出了参考物体的参考距离范围，DynamicBone的所有行为都会停止。
- **Reference Object 参考物体：**距离制机制的参考物体，如果为空则DynamicBone会选择场景内的主摄影机作为参考对象。
- **Distance To Object 参考距离：**距离控制机制的参考距离。
<a name="pPx8G"></a>
### 算法实现
<a name="TLoWl"></a>
#### 概览
计算惯性->计算受力（verlet：重力、摩擦力、阻力）-> 模拟弹性 -> 刚性还原（刚性偏移、碰撞、修正）<br />![](assets/post_images/Dynamic-Bones/image_003.webp#clientId=ude7aa300-e271-4&from=paste&id=u8f5d0f6f&originHeight=658&originWidth=1101&originalType=url&ratio=1.399999976158142&rotation=0&showTitle=false&status=done&style=none&taskId=ucc8433b9-7172-492b-82a6-6facf2a3603&title=)<br />![](assets/post_images/Dynamic-Bones/image_004.webp#clientId=ude7aa300-e271-4&from=paste&height=566&id=ud3dd9ba5&originHeight=576&originWidth=825&originalType=url&ratio=1.399999976158142&rotation=0&showTitle=false&status=done&style=none&taskId=ue0c92faf-af90-48b5-8a15-03687f7dbc4&title=&width=811)
<a name="u6GUM"></a>
#### 流程细节
<a name="kKEp2"></a>
##### 计算物体惯性
![](assets/post_images/Dynamic-Bones/image_005.svg#card=math&code=%5CDelta%20P%20%3D%20P%20-%20P%5E%7B%27%7D&id=Bbrna)
<a name="T4swO"></a>
##### 惯性模拟
![](assets/post_images/Dynamic-Bones/image_006.svg#card=math&code=P%20%3D%20P%20%2B%20%5CDelta%20P%20%2A%20inertia&id=M4wUY)<br />记录此时![](assets/post_images/Dynamic-Bones/image_007.svg#card=math&code=P%27%20%3D%20P&id=DAIEz)，以备后续循环使用。
<a name="eLwlU"></a>
##### 阻力模拟
![](assets/post_images/Dynamic-Bones/image_008.svg#card=math&code=P%20%3D%20P%20%2B%20%5CDelta%20P%20%2A%20%281-damping%29&id=fF5MB)
<a name="NCGtF"></a>
##### 受力模拟
![](assets/post_images/Dynamic-Bones/image_009.svg#card=math&code=f%20%3D%20%5Coverrightarrow%7Bg_%7B0%7D%7D%20-%20%20%20%5Cfrac%20%7B%5Coverrightarrow%7Bg_%7Blocal%7D%7D%7D%7Blen%28%5Coverrightarrow%7Bg_%7Blocal%7D%7D%29%7D%20%5Ccdot%20%5Coverrightarrow%7Bg_%7B0%7D%7D%20%20%2B%20f_%7Bexternal%7D&id=OcJ5s)<br />![](assets/post_images/Dynamic-Bones/image_010.svg#card=math&code=P%20%3D%20P%20%2B%20f%0A&id=FB574)<br />![](assets/post_images/Dynamic-Bones/image_011.webp#clientId=ude7aa300-e271-4&from=paste&id=u22a000ae&originHeight=417&originWidth=992&originalType=url&ratio=1.399999976158142&rotation=0&showTitle=false&status=done&style=none&taskId=ub141369c-6ce0-4115-bb97-d77439186e5&title=)
<a name="B0X9p"></a>
##### 弹性模拟
结合当前父节点的，算出该节点的理想位置![](assets/post_images/Dynamic-Bones/image_012.svg#card=math&code=P_%7Btar%7D&id=rdSLS)。<br />![](assets/post_images/Dynamic-Bones/image_013.svg#card=math&code=%5CDelta%20P_%7Btar%7D%20%3D%20P_%7Btar%7D%20-%20P&id=dkoS3)<br />![](assets/post_images/Dynamic-Bones/image_014.svg#card=math&code=P%20%3D%20P%20%2B%20%5CDelta%20P_%7Btar%7D%2Aelasticity&id=fh4d8)
<a name="b0gf6"></a>
##### 刚性模拟
![](assets/post_images/Dynamic-Bones/image_015.svg#card=math&code=l_%7B0%7D&id=T1U37)代表该段弹簧原长，父子节点间原本的距离  ![](assets/post_images/Dynamic-Bones/image_016.svg#card=math&code=l_%7B0%7D%20%3D%20len%28%20P_%7Bp0%7D%20-%20P_0%29&id=zi7C8)<br />![](assets/post_images/Dynamic-Bones/image_017.svg#card=math&code=l_%7Bmax%7D&id=iLVVx)为节点可偏离理想位置的最大距离 ![](assets/post_images/Dynamic-Bones/image_018.svg#card=math&code=l_%7Bmax%7D%20%3D%20l_0%20%2A%202%20%2A%20%281%20-%20stiffness%29&id=pamW7)<br />将节点限制在上述距离内 ![](assets/post_images/Dynamic-Bones/image_019.svg#card=math&code=P%20%3D%20P%20%2B%20%28P_%7Btar%7D%20-P%29%20%2A%20%5Cfrac%20%7Blen%28P_%7Btar%7D%20-%20P%29%20-%20l_%7Bmax%7D%7D%7Blen%28P_%7Btar%7D-P%29%7D&id=v4aFQ)
<a name="Zd6O8"></a>
##### 碰撞处理
提供sphere、capsule两种碰撞检测，如果嵌入，则直接penalty distance。
<a name="ylRv9"></a>
##### 保持节点距离
防止父子节点之间发生拉伸或压缩，**始终维持理想距离**。<br />![](assets/post_images/Dynamic-Bones/image_020.svg#card=math&code=P%20%3D%20P%20%2B%20%28P_p%20-%20P%29%20%2A%20%5Cfrac%7Blen%28P_p%20-%20P%29%20-%20l_0%7D%7Blen%28P_p%20-%20P%29%7D&id=vPge0)
<a name="YZgne"></a>
##### 修正旋转
计算原始子节点相对于父节点的位置 ![](assets/post_images/Dynamic-Bones/image_021.svg#card=math&code=%5CDelta%20D_%7B0%7D%20%3D%20P_%7B0%7D%20-%20P_%7Bp0%7D&id=rgtRN)<br />当前子节点相对于父节点的位置 ![](assets/post_images/Dynamic-Bones/image_022.svg#card=math&code=%5CDelta%20D%20%3D%20P%20-%20P_%7Bp%7D&id=Ba6kK)<br />让父节点的旋转与原始情况同步：![](assets/post_images/Dynamic-Bones/image_023.svg#card=math&code=P_%7Bp%7D%20%3D%20rotateFromTo%28%5CDelta%20D_0%2C%20%5CDelta%20D%29%20%2A%20P_p&id=Qepdf)
<a name="izCz7"></a>
### 优缺点
<a name="Xr5pj"></a>
#### 优点

- 参数少、使用友好。
- 实现简单、性能相对还可以，全程显式计算。
<a name="EBoDL"></a>
#### 缺点

- 缺乏弹簧的性质，不能模拟容易拉伸形变的物体。
- 计算过程没有时间概念（默认单位时间），导致调参难度大。
- 碰撞处理较为简单，仅支持球和胶囊体、且仅作用于指定的碰撞体上。
<a name="OmKfJ"></a>
#### 优化方向

- 性能：C++化、JobSystem、LOD降频
- 碰撞方面优化。
- 引入弹簧、隐式求解、XPBD（性能挑战）。
<a name="oEWfQ"></a>
## AnimDynamics (Unreal)
<a name="SkVFB"></a>
### INTRO
[AnimDynamics](https://docs.unrealengine.com/5.1/en-US/animation-blueprint-animdynamics-in-unreal-engine/)<br />![](assets/post_images/Dynamic-Bones/image_024.gif#clientId=u7b046daf-65b1-4&from=paste&id=u71fd1156&originHeight=300&originWidth=400&originalType=url&ratio=1.2000000476837158&rotation=0&showTitle=false&status=done&style=none&taskId=u87df1ded-83ce-4c7c-8608-08e2f6893ba&title=)<br />AnimDynamics是UE4.11 Preview 5测试版本开始，发布的AnimationBlueprint中的新节点。功能是通过简单物理模拟计算，更新骨骼位置。优点是避免了使用纯物理模拟时计算量过大，并且能实现近似物理效果。尤其用于悬垂物（辫子，锁链等自由下垂物体）上可以获得非常好的结果。<br />为了实现低开销，AnimDynamics节点采用了一些值得留意的近似解算方法：

- 使用**盒体**而非定义的动态骨骼来计算各节的惯性。
- 不计算碰撞。相反，使用**约束**来限制移动。
<a name="ZVXDg"></a>
### 工作流
<a name="pD8ZC"></a>
#### 基本操作
AnimDynamics节点支持线性约束、角约束和平面约束，以便模拟基于物理的的运动。**线性（Linear）** 和 **角（Angular）** 约束可以受弹簧的驱动，提供更有弹性的感觉，而 **平面（Planar）** 约束可用于创建对象不会穿过的平面。<br />![](assets/post_images/Dynamic-Bones/image_025.jpeg#clientId=u950b3e5d-3588-4&from=paste&id=uae307691&originHeight=552&originWidth=989&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u7900d56b-d4b2-4512-87e3-313e4f124f8&title=)<br />在AnimDynamics节点里，能够绑定RigidBody关联到指定Bone上，通过计算RigidBody的动量，在风，重力影响下更新动量，以及考虑附加的线性和角度的Limit，刷新Bone和RigidBody的位置。<br />通过启用 **链（Chain）** 属性，并选择 **边界骨骼（Bound Bone）** 和 **链端（Chain End）** ，Anim Dynamics将使用两者之间的骨骼生成链。除了 **边界骨骼（Bound Bone）** 之外，链中的每块骨骼都将在其上方生成一个约束盒体，以模拟与链中其他骨骼的运动和碰撞。这些约束盒体需要手动调整才能实现不错的效果。<br />![](assets/post_images/Dynamic-Bones/image_026.gif#clientId=u950b3e5d-3588-4&from=paste&id=ucd5d7a94&originHeight=500&originWidth=700&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u6b8f5556-7d98-47e9-a740-dfb0343b8ac&title=)
<a name="Xxadf"></a>
#### 碰撞模拟

- **平面限制**：将平面限制添加到角色的 **根骨骼** ，可以创建对象无法跨越的地面边界，以防结构看起来穿过了游戏世界的地面。

![](assets/post_images/Dynamic-Bones/image_027.jpeg#clientId=u950b3e5d-3588-4&from=paste&id=u73f385e3&originHeight=344&originWidth=667&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=uaf227442-17cc-4aa1-a4fd-683670dc9ca&title=)

- **球体限制：**借助球体限制，你可以设置球体来包围模拟结构上的点，充当简单的碰撞预防，实现更动态的互动。

![](assets/post_images/Dynamic-Bones/image_028.jpeg#clientId=u950b3e5d-3588-4&from=paste&id=u2761976b&originHeight=700&originWidth=823&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u87485f14-f72b-4263-a891-729f3601d56&title=)<br />![](assets/post_images/Dynamic-Bones/image_029.gif#clientId=u950b3e5d-3588-4&from=paste&height=303&id=ua74cf4cc&originHeight=256&originWidth=296&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u5cb31d15-7d91-4f5a-a17b-5ea38a3bca4&title=&width=350)![](assets/post_images/Dynamic-Bones/image_030.gif#clientId=u950b3e5d-3588-4&from=paste&height=303&id=u455a24eb&originHeight=288&originWidth=333&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u28567d60-9291-4081-a213-97e2ea75abf&title=&width=350)

<a name="vhExw"></a>
#### 属性参数

- **Chain **：是否使用链式Body绑定。若true则Bound Bone是Chain起点，Chain End是Chain终点，链中每个Bone都会绑上一个RigidBody。若false则只能选择BoundBone，对单个Bone绑定控制。
- **Bound Bone ：**Body绑定的骨骼
- **Chain End ：**使用链子时的终点
- **Box Extents ：**Body的ShapeBox的大小，用于计算惯性张量InverseTensor。Box体积大小与惯性大小成正比。
- **Local Joint Offset ：**Body相对于Bone的偏移值。偏移后类似于钟摆效果。
- **Gravity Scale ：**重力作用比例，重力大小使用UPhysicsSetting中的Gravity
- **Linear Spring ：**是否线性反弹，body会尝试弹回初始位置
- **Angular Spring ：**是否角度反弹，body会尝试和指定角度目标一致
- **Linear Spring Constant ：**计算线性反弹时的系数，越大反弹力越强
- **Angular Spring Constant ：**计算角度反弹时的系数，越大反弹力越强
<a name="HGGA3"></a>
### 算法实现
<a name="ugOTs"></a>
#### 基于box的惯性更新
```cpp
FVector Force = FVector(0.0f, 0.0f,UPhysicsSettings::Get()->DefaultGravityZ) * InBody->Mass *InBody->GravityScale;
Force += WindVelocity *InBody->WindData.WindAdaption;
InBody->LinearMomentum += Force *DeltaTime;
InBody->NextPosition =InBody->Pose.Position + InBody->LinearMomentum * InBody->InverseMass *DeltaTime;
```
<a name="qF0SF"></a>
#### 使用约束限制移动
```cpp
void FAnimNode_AnimDynamics::UpdateLimits(FComponentSpacePoseContext& Output)
{
	...
	const FAnimPhysBodyDefinition& PhysicsBodyDef = PhysicsBodyDefinitions[ActiveIndex];
	...
			if (PhysicsBodyDef.ConstraintSetup.bLinearFullyLocked)
		{
			// Rather than calculate prismatic limits, just lock the transform (1 limit instead of 6)
			FAnimPhys::ConstrainPositionNailed(NextTimeStep, LinearLimits, PrevBody, ShapeTransform.GetTranslation(), &RigidBody, Body1JointOffset);
		}
		else
		{
			//  线速度
			if (PhysicsBodyDef.ConstraintSetup.LinearXLimitType != AnimPhysLinearConstraintType::Free)
			{
				FAnimPhys::ConstrainAlongDirection(NextTimeStep, LinearLimits, PrevBody, ShapeTransform.GetTranslation(), &RigidBody, Body1JointOffset, ShapeTransform.GetRotation().GetAxisX(), FVector2D(PhysicsBodyDef.ConstraintSetup.LinearAxesMin.X, PhysicsBodyDef.ConstraintSetup.LinearAxesMax.X));
			}
			...
		}

	...
		// 平面限制
		if(PlanarLimits.Num() > 0 && bUsePlanarLimit)
		{
			for(FAnimPhysPlanarLimit& PlanarLimit : PlanarLimits)
			{
				...
				FAnimPhys::ConstrainPlanar(NextTimeStep, LinearLimits, &RigidBody, LimitPlaneTransform);
			}
		}
		// 球体限制
		if(SphericalLimits.Num() > 0 && bUseSphericalLimits)
		{
			for(FAnimPhysSphericalLimit& SphericalLimit : SphericalLimits)
			{
				...
				switch(SphericalLimit.LimitType)
				{
				case ESphericalLimitType::Inner:
					FAnimPhys::ConstrainSphericalInner(NextTimeStep, LinearLimits, &RigidBody, SphereTransform, SphericalLimit.LimitRadius);
					break;
				case ESphericalLimitType::Outer:
					FAnimPhys::ConstrainSphericalOuter(NextTimeStep, LinearLimits, &RigidBody, SphereTransform, SphericalLimit.LimitRadius);
					break;
				default:
					break;
				}
			}
		}
}

```
<a name="zGxH1"></a>
### 优缺点
<a name="pEqXL"></a>
#### 优点

- 轻量级、计算快。
- 设计合理：骨骼惯性+约束，美术友好。
<a name="yzUwj"></a>
#### 缺点

- 碰撞检测不ok。
- 约束调节需要经验。
- 还是假。

![](assets/post_images/Dynamic-Bones/image_031.gif#clientId=u950b3e5d-3588-4&from=paste&id=ud3845a9a&originHeight=288&originWidth=316&originalType=url&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&taskId=u60bead0b-016f-47ac-9331-b83a047d198&title=)
<a name="M30hY"></a>
## OpenSource
<a name="AexyZ"></a>
### JointDynamics
[GitHub - SPARK-inc/SPCRJointDynamics: 布風骨物理エンジン](https://github.com/SPARK-inc/SPCRJointDynamics)<br />![physics.gif](assets/post_images/Dynamic-Bones/image_032.gif#clientId=u5a5dbcdc-ee2f-4&from=drop&id=u7128d2a3&originHeight=350&originWidth=600&originalType=binary&ratio=1.2000000476837158&rotation=0&showTitle=false&size=37755043&status=done&style=none&taskId=uc83ba475-8e0d-4608-a33b-655095201b6&title=)
<a name="KL9FP"></a>
#### 工作流

- 为所有需要期待影响的骨骼添加 SPCRJointDynamicsPoint 组件。

![SpcrJointDynamcis_1.png](assets/post_images/Dynamic-Bones/image_033.png#clientId=u5f1033ca-072c-4&from=drop&id=u9a01c727&originHeight=614&originWidth=717&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=134150&status=done&style=none&taskId=u38777ba8-3035-4312-ba51-544cd3a3484&title=)

- 角色根节点添加 SPCRJointDynamicsController组件；并设置 Parent Transform。

![SpcrJointDynamcis_2.png](assets/post_images/Dynamic-Bones/image_034.png#clientId=u5f1033ca-072c-4&from=drop&id=ufab10078&originHeight=564&originWidth=719&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=146621&status=done&style=none&taskId=u4a172f59-487e-494f-98fc-22c1b32b62f&title=)

- 点击 Automatically detect the root points，自动配置子骨骼列表，并将根骨骼添加到列表中的子节点中。

![SpcrJointDynamcis_3.png](assets/post_images/Dynamic-Bones/image_035.png#clientId=u5f1033ca-072c-4&from=drop&id=u5ebefbf0&originHeight=437&originWidth=786&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=131622&status=done&style=none&taskId=u977fa9f7-1cf5-4415-8da7-c3796ce0d9f&title=)

- 在Controller中，设置相关约束参数（弹簧等）。

![SpcrJointDynamcis_4.png](assets/post_images/Dynamic-Bones/image_036.png#clientId=u5f1033ca-072c-4&from=drop&id=ubaa9519d&originHeight=437&originWidth=789&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=106522&status=done&style=none&taskId=ube074231-e2d0-4bb5-900b-85d42501e49&title=)

- 添加碰撞体。

![SPCRJointynamicsColliderAdd.png](assets/post_images/Dynamic-Bones/image_037.png#clientId=u5f1033ca-072c-4&from=drop&id=u3a38fc37&originHeight=347&originWidth=314&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=37804&status=done&style=none&taskId=u2f22af71-9b9d-488f-8c00-9ed4c20a4bf&title=)![SPCRJointColliderSetting.png](assets/post_images/Dynamic-Bones/image_038.png#clientId=u5f1033ca-072c-4&from=drop&height=141&id=u3021e4a2&originHeight=190&originWidth=379&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=9378&status=done&style=none&taskId=uc2007127-14b6-4d15-9a8a-a6a02371485&title=&width=280.9861145019531)
<a name="Yd63W"></a>
##### 参数列表
![SPCRJointDynamicsEachParameter.png](assets/post_images/Dynamic-Bones/image_039.png#clientId=u5f1033ca-072c-4&from=drop&id=u58e2ccf2&originHeight=2609&originWidth=1069&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=328056&status=done&style=none&taskId=u03e49573-51dd-4caa-942c-4b353dde706&title=)
<a name="Q3Nga"></a>
#### 算法实现
<a name="pAEc4"></a>
##### 弹簧系统
![SpcrJointDynamcis.png](assets/post_images/Dynamic-Bones/image_040.png#clientId=u982580dc-cf03-4&from=drop&id=u205d0ce5&originHeight=603&originWidth=916&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=128574&status=done&style=none&taskId=u907cd8ac-d6b5-489d-aaac-f2200f5a5ab&title=)
<a name="CD2fS"></a>
##### 大致流程

- 获取节点移动及旋转等。
- 更新节点碰撞体（capsule）。
- 类似DynamicBone的方法，更新节点位置（惯性、摩擦力、重力、其他外力等）。
- 处理表面碰撞（checkCollision->capusle的精确碰撞）。
- 迭代求解约束，显式求解。![](assets/post_images/Dynamic-Bones/image_041.svg#card=math&code=%5CDelta%20d%20%3D%20%20direction%28P_0%20-%20P_1%29%20%2A%20%28%5CDelta%20l%20%2A%20c%29&id=wimp0)
- 处理碰撞体间碰撞。
- 更新位置、记录速度。

![image.png](assets/post_images/Dynamic-Bones/image_042.png#clientId=u99d481e1-e092-4&from=paste&height=439&id=ub9f95d4f&originHeight=593&originWidth=895&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=149015&status=done&style=none&taskId=uf7208d91-356a-4718-939a-4535f74e43a&title=&width=662.9630097963552)
<a name="v5s1y"></a>
#### 特点

- 使用**JobSystem**实现加速。
- 考虑了柔体的弹性，保证**效率**同时，得到了还不错的结果。
- 工作流相对简洁，但对使用者来说有一定**成本**，要添加节点、调整各种弹簧参数。
- 效果会比DynamicBone更加**丰富**，但处理精细碰撞会导致效率**更低**。
<a name="N2BtN"></a>
### SoftBone
[GitHub - EZhex1991/EZSoftBone: A simple kinetic simulator for Unity, you can use it to simulate hair/tail/breast/skirt and other soft objects](https://github.com/EZhex1991/EZSoftBone)<br />![EZSoftBone_2.gif](assets/post_images/Dynamic-Bones/image_043.gif#clientId=uf4e54c24-1d96-4&from=drop&id=fOmQs&originHeight=240&originWidth=426&originalType=binary&ratio=1.2000000476837158&rotation=0&showTitle=false&size=2824691&status=done&style=none&taskId=ue1f67e24-c6a1-454f-b3f2-256c0c1bf04&title=)![EZSoftBone_3.gif](assets/post_images/Dynamic-Bones/image_044.gif#clientId=uf4e54c24-1d96-4&from=drop&id=hBF7D&originHeight=240&originWidth=426&originalType=binary&ratio=1.2000000476837158&rotation=0&showTitle=false&size=421035&status=done&style=none&taskId=u74ae1293-c4d2-4797-abd5-da61ce1358c&title=)

- All colliders supported (include MeshCollider)
- Net structure supported (Cloth simulation)
- Use EZSoftBoneMaterial to adjust effects, and reuse it on other EZSoftBones
- Inherit EZSoftBoneColliderBase to create custom colliders
- Beautiful wind simulator
<a name="pI8bU"></a>
#### 工作流

- 设置骨骼的变换设置骨骼材质（可复用）
- 设置外部碰撞体
- 设置系统外力（重力、风力等）

![EZSoftBone_Inspector.png](assets/post_images/Dynamic-Bones/image_045.png#clientId=u99d481e1-e092-4&from=ui&id=u4049a8ca&originHeight=799&originWidth=462&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=64375&status=done&style=none&taskId=ub8542574-10c2-4fa2-a394-72aecc067b3&title=)
<a name="zsQ5r"></a>
#### 算法实现

- 通过Resistance、Damping、Stiffness、Slackness，更新bone的位移。
- 通过弹簧约束，更新两端bone的位置（显式）。
- 碰撞检测并进行响应。
- 记录速度，更新位置。
```cpp
Vector3 oldWorldPosition, newWorldPosition, expectedPosition;
oldWorldPosition = newWorldPosition = bone.worldPosition;

// Resistance (force resistance)
Vector3 force = globalForce;
if (forceModule != null && forceModule.isActiveAndEnabled)
{
    force += forceModule.GetForce(bone.normalizedLength) * forceScale;
}
if (customForce != null)
{
    force += customForce(bone.normalizedLength);
}
force.x *= transform.localScale.x;
force.y *= transform.localScale.y;
force.z *= transform.localScale.z;
bone.speed += force * (1 - bone.resistance) / iterations;

// Damping (inertia attenuation)
bone.speed *= 1 - bone.damping;
if (bone.speed.sqrMagnitude > sleepThreshold)
{
    newWorldPosition += bone.speed * deltaTime;
}

// Stiffness (shape keeper)
Vector3 parentMovement = bone.parentBone.worldPosition - bone.parentBone.transform.position;
expectedPosition = bone.parentBone.transform.TransformPoint(bone.localPosition) + parentMovement;
newWorldPosition = Vector3.Lerp(newWorldPosition, expectedPosition, bone.stiffness / iterations);

// Slackness (length keeper)
// Length needs to be calculated with TransformVector to match runtime scaling
Vector3 dirToParent = (newWorldPosition - bone.parentBone.worldPosition).normalized;
float lengthToParent = bone.parentBone.transform.TransformVector(bone.localPosition).magnitude;
expectedPosition = bone.parentBone.worldPosition + dirToParent * lengthToParent;
int lengthConstraints = 1;
// Sibling constraints
if (siblingConstraints != UnificationMode.None)
{
    if (bone.leftBone != null)
    {
        Vector3 dirToLeft = (newWorldPosition - bone.leftBone.worldPosition).normalized;
        float lengthToLeft = bone.transform.TransformVector(bone.leftPosition).magnitude;
        expectedPosition += bone.leftBone.worldPosition + dirToLeft * lengthToLeft;
        lengthConstraints++;
    }
    if (bone.rightBone != null)
    {
        Vector3 dirToRight = (newWorldPosition - bone.rightBone.worldPosition).normalized;
        float lengthToRight = bone.transform.TransformVector(bone.rightPosition).magnitude;
        expectedPosition += bone.rightBone.worldPosition + dirToRight * lengthToRight;
        lengthConstraints++;
    }
}
expectedPosition /= lengthConstraints;
newWorldPosition = Vector3.Lerp(expectedPosition, newWorldPosition, bone.slackness / iterations);

// Collision
if (bone.radius > 0)
{
    foreach (EZSoftBoneColliderBase collider in EZSoftBoneColliderBase.EnabledColliders)
    {
        if (bone.transform != collider.transform && collisionLayers.Contains(collider.gameObject.layer))
            collider.Collide(ref newWorldPosition, bone.radius);
    }
    foreach (Collider collider in extraColliders)
    {
        if (bone.transform != collider.transform && collider.enabled)
            EZSoftBoneUtility.PointOutsideCollider(ref newWorldPosition, collider, bone.radius);
    }
}

bone.speed = (bone.speed + (newWorldPosition - oldWorldPosition) / deltaTime) * 0.5f;
bone.worldPosition = newWorldPosition;
```
<a name="bJHi8"></a>
#### 特点
与JointDynamics精神上基本一致，但没有实现JobSystem，力学方程相对简单。
<a name="N2zqI"></a>
### KawaiiPhysics
assets/post_images/Dynamic-Bones/image_046.[GitHub - pafuhana1213/KawaiiPhysics: KawaiiPhysics : Simple fake Physics for UnrealEngine4 & 5](https://github.com/pafuhana1213/KawaiiPhysics)<br />![](https://github.com/pafuhana1213/Screenshot/raw/master/KawaiiPhysics2.jpg#from=url&id=HKTAj&originHeight=761&originWidth=1694&originalType=binary&ratio=1.5749999284744263&rotation=0&showTitle=false&status=done&style=none&title=)<br />是AnimDynamics的加强版，工作流与AnimDynamics一致，但效果更好。<br />![KawaiiPhysics0.gif](assets/post_images/Dynamic-Bones/image_047.gif#clientId=u982580dc-cf03-4&from=drop&id=u5f2f5220&originHeight=270&originWidth=480&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=2351667&status=done&style=none&taskId=uda5849b6-9059-4a4a-bdbb-f9b5f50e6c9&title=)![KawaiiPhysics1.gif](assets/post_images/Dynamic-Bones/image_048.gif#clientId=u982580dc-cf03-4&from=drop&id=uca11ac29&originHeight=270&originWidth=480&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=1878281&status=done&style=none&taskId=u690cef76-7378-4969-9a93-72777991449&title=)![KawaiiPhysics4.gif](assets/post_images/Dynamic-Bones/image_049.gif#clientId=u982580dc-cf03-4&from=drop&id=u6b90d312&originHeight=353&originWidth=500&originalType=binary&ratio=1.3499999046325684&rotation=0&showTitle=false&size=4840594&status=done&style=none&taskId=ucb818d2b-a8b0-4206-80b9-4230490d1ca&title=)


<a name="GS8y4"></a>
## 思考

- 基于约束的刚性及显式求解的精髓？
   - **稳定**！稳定！还是稳定！**快速**！快速！还是快速！ 牺牲真实感换来的安心。
- 效果更好的Magic Cloth对比，性能开销大很多（数倍）。

[Magica Cloth_UWA的博客-CSDN博客](https://blog.csdn.net/UWA4D/article/details/127788816)

- 为什么要把旋转反作用回父节点？
   - 将子节点相对父节点的向量旋转，作用于父节点中，为了保持局部蒙皮的**平滑**，否则在节点处会有突兀感。

![image.png](assets/post_images/Dynamic-Bones/image_050.png#clientId=uddccf573-fc14-4&from=paste&height=856&id=uf9a129da&originHeight=1348&originWidth=2145&originalType=binary&ratio=1.5749999284744263&rotation=0&showTitle=false&size=748958&status=done&style=none&taskId=u4a638778-dc81-45b5-9fb6-1d26bef3d6b&title=&width=1361.904823753031)<br />![image.png](assets/post_images/Dynamic-Bones/image_051.png#clientId=uddccf573-fc14-4&from=paste&height=999&id=u1c14a171&originHeight=1348&originWidth=2145&originalType=binary&ratio=1.5749999284744263&rotation=0&showTitle=false&size=738091&status=done&style=none&taskId=u4ec466eb-b960-4d4b-a222-950203320a4&title=&width=1588.8890011320468)
<a name="AHBqH"></a>
## References

- [Verlet Integration – A Case Study of Simple Dynamic Bone](https://tedsieblog.wordpress.com/2020/03/10/verlet-integration-a-case-study-of-simple-dynamic-bone/)

- [动态骨骼Dynamic Bone算法详解](https://zhuanlan.zhihu.com/p/49188230)
