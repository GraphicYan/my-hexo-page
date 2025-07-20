---
title: 仿真及动力学系统综述
layout: Simulation Dynamics Engine
toc: true
top: true
date: 2023/06/04 11:23:25
---

### 原创性声明
本文为作者原创，在个人Blog首次发布，如需转载请注明引用出处。（yanzhang.cg@gmail.com 或 https://graphicyan.github.io/）

<a name="FOuW4"></a>
### 0 引言
![image.png](assets/post_images/Simulation-Dynamics-Engine/image_000.png#clientId=u90167c2b-ba94-4&from=paste&height=309&id=u1909dd33&originHeight=579&originWidth=653&originalType=binary&ratio=1&rotation=0&showTitle=false&size=106557&status=done&style=none&taskId=uf2a046cf-0270-4579-9656-3ba571de90a&title=&width=348.26666666666665)
<a name="DUUJS"></a>
### 1 物理引擎综述
<a name="DeeBQ"></a>
#### 1.1 常见的物理引擎
下图中展示了常见的物理引擎，关于其性能分析可见文献[1]。其中ODE、Bullet、DART消费级机器人仿真中应用广泛，OpenSim用于人体肌肉组织仿真，MuJoCo([**/mud͡ʒowkow/**](https://www.howtopronounce.com/mujoco))主要应用于强化学习和最优化控制领域，RaiSim是ETH Robotic Systems Lab开发的目前最新的物理引擎，应用于他们实验室开发的四足机器人ANYmal。Bullet、PhysX、Havok应用于游戏，Bullet由于版权优势在一些机器人领域有替代MuJoCo趋势。Flex是NVIDIA开发的引擎,在流体模拟、NVIDIA自家的GPU加速方面有优势，NVIDIA内部研究机构也有尝试应用于机器人[2]。<br />![](assets/post_images/Simulation-Dynamics-Engine/image_001.webp#clientId=u526a2707-d8ac-4&from=paste&id=XB44T&originHeight=1292&originWidth=1440&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ud26d58f1-4734-4a68-a7e7-ec0c1d1c4aa&title=)
<a name="AHsTm"></a>
##### ODE
 	[ODE](https://www.ode.org/) is an **open-source** physics engine. It is probably the engine most commonly used in robotics applications, most notably in the VRC. It is integrated with Gazebo and V-REP, as well as other robotics frameworks. ODE implements a **sophisticated integrator** for angular DOFs, a feature that contributes to its performance in the energy and angular momentum tests. ODE has an **iterative solver** and an **exact solver**. As part of the VRC effort, OSRF has developed implicit damping for ODE (John Hsu, personal communication) but this has not yet been merged with the main version in the official repository.
<a name="ImJd2"></a>
##### Bullet
 	[Bullet ](https://pybullet.org/wordpress/)is another **open-source** physics engine that is also integrated with many of the popular robotics software platforms, including V-REP and Gazebo. While Bullet has built-in functionality for **spring-dampers** at hinge joints, its damping functionality does not conform to the standard PD controller design pattern: it is impulsebased, and therefore uses abnormal units to specify damping (instead of using Nms/rad, the damper’s parameter roughly corresponds to “what fraction of the velocity should be retained in the next timestep”).  
<a name="T0q9h"></a>
##### PhysX
 	[PhysX](https://github.com/NVIDIA-Omniverse/PhysX) together with Havok, is among the most widely used gaming engines. It also makes the most drastic compromises in terms of physical accuracy – in particular it **ignores** **Coriolis forces** . This alone makes it unsuitable for robotics applications where accuracy is important. While PhysX supports hinge joints, we used a constrained 6D joint instead for the benefit of using a built-in PD controller class PxD6Drive. We also implemented an articulation-based instance, but we experienced several difficulties: first, articulation joints have 3 DOFs, so in order to create a hinge we had to impose artificially-tight swing limits. Furthermore, the articulation API does not offer a direct way to compute joint angles. We therefore do not include these results in our comparisons.  
<a name="oX3H3"></a>
##### Havok
  	[Havok](https://www.havok.com/) also ignores Coriolis forces, and therefore is also unsuitable to applications where accuracy is important. Note however that a Havok engineer suggested a possible way to manually introduce such forces . Havok does not support plane geometries, and therefore we implemented the ground plane using a big box, setting the collision margin (setRadius) to 0. The Havok API does not provide a way to query the angle of a hinge constraint; we tried to implement this feature in several ways, including following the example of ODE’s codebase and advice from Havok engineers on the developers’ forum , but none of these solutions worked well enough. Therefore, we currently have no working PD controller for Havok, and it is therefore excluded from the grasping test in the current version.  
<a name="wV1xr"></a>
##### MuJoCo
 	[MuJoCo](https://mujoco.org/) is the engine we have developed and used extensively in our research over the past 5 years. MuJoCo has a built-in implementation of Hinge PD controllers that uses implicit damping. We present results for two versions of MuJoCo, using the semi-implicit Euler intrator vs. the 4th-order Runge-Kutta integrator.  
<a name="hBUzs"></a>
#### 1.2 游戏物理 vs 机器人仿真
游戏市场对机器人仿真领域冲击很大。积极上说，游戏产业的发展加速了对物理现象仿真的研究，并且随着游戏物理引擎逼真度的提升，越来越多的功能被应用在机器人仿真领域。不过机器人仿真跟游戏还是有上述本质区别，最基本的从底层力学工具就已经完全区分开: 正经的 **游戏物理引擎** 一般不过多考虑刚体系统的性能优化，采用简单的**牛顿力学**工具，有助于游戏开发者理解原理；**机器人物理引擎 **则倾向于采用[Featherstone的空间向量方法](https://www.zhihu.com/column/c_1376840673417629696)(如下图)，保证尽可能高效的**刚体动力学**算法实现(如MuJoCo、RaiSim)。<br />![image.png](assets/post_images/Simulation-Dynamics-Engine/image_002.png#clientId=u90167c2b-ba94-4&from=paste&id=u2a0139b2&originHeight=453&originWidth=720&originalType=url&ratio=1&rotation=0&showTitle=false&size=559706&status=done&style=none&taskId=u5a4a30dc-7794-47a5-802f-6e72280db04&title=)<br />游戏引擎侧重点在**视觉上的真实感**。<br />机器人引擎（动力学仿真）侧重点在**物理上的正确性**。
<a name="LXnMQ"></a>
#### 1.3 机器人仿真
机器人物理引擎狭义上仅对刚体前向动力学的模拟器,如[ODE](https://www.ode.org/)。这种物理引擎输入用户端控制量(如关节电机力矩、空间作用力)，对刚体系统碰撞、接触和力学进行解算，输出整个系统的加速度，再通过积分器得到下一个系统状态，相关算法可参考[前向动力学](https://zhuanlan.zhihu.com/p/375456579)。如Gazebo、V-rep这些仿真器内置了多种常见物理引擎，可以让用户自行选择。<br />广义上的物理引擎还需要上述传感器、驱动器、视觉渲染等模块，此时物理引擎更倾向于一种轻量的仿真器。比如 MuJoCo 即属于这种广义物理引擎，可以将引擎模块用于其他仿真器中(如集成在[Unity](http://www.mujoco.org/book/unity.html))，也可以直接用物理引擎来做仿真，如[pybullet](https://pybullet.org/wordpress/)。

<a name="pvjqO"></a>
#### 1.4 机器人引擎数据对比
From：机器人及专业动力学仿真需求人士调研问卷[1]。
<a name="Vmi5s"></a>
##### 1.4.1 使用率
![image.png](assets/post_images/Simulation-Dynamics-Engine/image_003.png#clientId=u90167c2b-ba94-4&from=paste&height=386&id=uc20385bc&originHeight=724&originWidth=1031&originalType=binary&ratio=1&rotation=0&showTitle=false&size=323468&status=done&style=none&taskId=u91104bfb-eceb-4b2b-aee2-f78108155c2&title=&width=549.8666666666667)
<a name="X294X"></a>
##### 1.4.2 特性排序
![image.png](assets/post_images/Simulation-Dynamics-Engine/image_004.png#clientId=u90167c2b-ba94-4&from=paste&height=148&id=ud7e24a0f&originHeight=277&originWidth=1207&originalType=binary&ratio=1&rotation=0&showTitle=false&size=146538&status=done&style=none&taskId=u7d881819-8f2f-4015-b708-2238415897a&title=&width=643.7333333333333)
<a name="nSf6q"></a>
##### 1.4.3 仿真效率对比

- Grasping (35-DOF Robotic Arm)

![image.png](assets/post_images/Simulation-Dynamics-Engine/image_005.png#clientId=u90167c2b-ba94-4&from=paste&height=212&id=ud7ca0cd1&originHeight=398&originWidth=1191&originalType=binary&ratio=1&rotation=0&showTitle=false&size=148884&status=done&style=none&taskId=u70d0823a-5e77-46c0-a667-4934f98fcd0&title=&width=635.2)

- Humanoid (25-DOF Humanoid)

![image.png](assets/post_images/Simulation-Dynamics-Engine/image_006.png#clientId=u90167c2b-ba94-4&from=paste&height=214&id=u146d348f&originHeight=402&originWidth=1182&originalType=binary&ratio=1&rotation=0&showTitle=false&size=217706&status=done&style=none&taskId=ud6678dd3-6c5e-4769-9fcb-9a6639974c1&title=&width=630.4)

- Planar Chain (5-DOF Planar Kinematic Chain)

![image.png](assets/post_images/Simulation-Dynamics-Engine/image_007.png#clientId=u90167c2b-ba94-4&from=paste&height=211&id=u920513f5&originHeight=395&originWidth=1178&originalType=binary&ratio=1&rotation=0&showTitle=false&size=161735&status=done&style=none&taskId=u1dbad2ee-fff3-4ec4-9134-ec429b82f84&title=&width=628.2666666666667)

- 27 Capsules (Randomly-oriented capsules, 27x6 = 162DOFs)

![image.png](assets/post_images/Simulation-Dynamics-Engine/image_008.png#clientId=u90167c2b-ba94-4&from=paste&height=218&id=ub191d326&originHeight=408&originWidth=1188&originalType=binary&ratio=1&rotation=0&showTitle=false&size=242638&status=done&style=none&taskId=u7bbeac79-e000-4be9-8776-13f8c361241&title=&width=633.6)<br />MuJoCo 遥遥领先[6]。

<a name="K288F"></a>
#### 1.5 学界研究方向
<a name="Q9dmh"></a>
##### 1.5.1 传统仿真
数学模型为王，spring-mass, PBD，x-CCD，[IPC](https://ipc-sim.github.io/C-IPC/)等。<br />![image.png](assets/post_images/Simulation-Dynamics-Engine/image_009.png#clientId=u90167c2b-ba94-4&from=paste&height=301&id=u01fd0b96&originHeight=565&originWidth=1292&originalType=binary&ratio=1&rotation=0&showTitle=false&size=485742&status=done&style=none&taskId=u80dcecff-6932-42ea-a9c9-7953d66c1b1&title=&width=689.0666666666667)
<a name="M3YK5"></a>
##### 1.5.2 可微方向（AI)
目前在机器人初现的是将物理引擎跟控制结合起来。如强化学习中默认环境转移 P(st+1|st,at) 是黑箱，即使对环境建模也只是通过采样方法得到一个环境近似模型(即基于模型强化学习)，并没有利用到物理建模的先验知识。最近的研究如将**物理引擎**变成**可微分形式**[3], 将**控制**看成一个结合**环境模型**的优化问题[4]，可以将控制和物理仿真结合在一起。另外就是减小sim-to-real gap。因为物理引擎内部已经建立了环境的系统模型，一些机器人标定、辨识的[底层工具箱](https://roboti.us/optico.html)完全可以整合在引擎中。

<a name="EUk6w"></a>
### 2 MuJoCo
<a name="ddZvU"></a>
#### 2.1 简介
MuJoCo is a free and open source physics engine that aims to facilitate research and development in robotics, biomechanics, graphics and animation, and other areas where fast and accurate simulation is needed.<br />[https://mujoco.org/](https://mujoco.org/)<br />[https://github.com/deepmind/mujoco](https://github.com/deepmind/mujoco)<br />MuJoCo全称为Multi-Joint dynamics with Contact，主要由华盛顿大学的Emo Todorov教授开发，应用于最优控制、状态估计、系统辨识等领域，在机器人动态多点接触的应用场合(如多指灵巧手操作)有明显优势。不同于其他引擎采用urdf或者sdf等机器人模型， MuJoCo引擎团队自己开发了一种机器人的建模格式(**MJCF**)，来支持更多的环境参数配置。另外开发者**提出了一种全新的soft contact模型，来表征复杂的柔性表面接触和摩擦力**,以此推导出全新的约束求解器和动力学模型,详细内容可见文献[5] (该文献也是笔者读过的最叹为观止的机器人领域论文，短短八页内容出现了近50个公式)。为了提高仿真性能，MuJoCo做了**AVX指令**等大量优化，是极少的选择C语言来实现的现代物理引擎之一。

<a name="KqmqX"></a>
#### 2.2 核心特点

- Simulation in **generalized coordinates**, avoiding joint violations
- **Inverse dynamics** that are well-defined even in the presence of contacts
- Unified continuous-time formulation of constraints via **convex optimization**
- **Constraints** include soft contacts, limits, dry friction, equality constraints
- Simulation of particle systems, cloth, rope and soft objects
- Actuators including motors, cylinders, muscles, tendons, slider-cranks
- Choice of Newton, Conjugate Gradient, or Projected Gauss-Seidel **solvers**
- Choice of pyramidal or elliptic friction cones, dense or sparse Jacobians
- Choice of Euler or Runge-Kutta numerical **integrators**
- Multi-threaded sampling and finite-difference approximations
- Intuitive **XML** model format (called MJCF) and built-in model compiler
- Cross-platform GUI with interactive 3D visualization in OpenGL
- Run-time module written in ANSI C and hand-tuned for performance

<a name="AeFyg"></a>
##### 2.2.1 结合先进接触力学、广义坐标系统

- 游戏引擎(如ODE、Bullet、Physx)一般通过数值优化的方法来处理关节约束，会造成多刚体系统的不稳定和不精确。MuJoCo则采用广义坐标系和基于优化方法的接触力学方法。
<a name="e48XM"></a>
##### 2.2.2 柔性、凸模型并且解析可逆的接触力学

- 现代物理引擎大多数[求解线性互补问题](https://zhuanlan.zhihu.com/p/378361153)来处理约束，MuJoCo允许软体接触和其他约束，并包含一个独有的逆动力学模型来做数据分析。提出了新的摩擦力模型，支持滚动摩擦、扭转摩擦等多种摩擦力仿真。
<a name="fh0M5"></a>
##### 2.2.3 肌腱仿真

- MuJoCo支持3D的肌腱模型，这个模型跟OpenSim的肌肉模型相关，不过做了进一步优化，使MuJoCo支持人工肌肉仿真、线驱动灵巧手仿真等实用功能。
<a name="XiIxt"></a>
##### 2.2.4 广义驱动器模型

- 可以配置高达3阶的驱动器模型，从而实现气缸、液压、肌肉等各种非线性驱动器仿真。
<a name="Uv2Ex"></a>
##### 2.2.5 可灵活配置的仿真流程

- 可能灵活将仿真步骤拆开执行，或者只执行仿真流程的一部分(如不计算逆动力学)。
<a name="fVLFv"></a>
##### 2.2.6 先进的模型、编译方法

- 采用mjModel、mjData分离模型和运行时数据，有助于并行。模型可以编译成MJB二进制格式文件，提高加载速度。
<a name="bvVvR"></a>
##### 2.2.7 强大的环境建模语言

- 独创了MJCF建模格式，相比URDF模型具有易读性、灵活配置等优点。
<a name="ATo5y"></a>
##### 2.2.8 高效的软体材料仿真

- 支持绳、布料、可变3D物体的稳定可靠仿真。
<a name="taWv2"></a>
#### 2.3 对比游戏引擎

- **Gaming engines** use a more modern approach where contact forces are found by solving an **optimization problem**. However, they often resort to the over-specified **Cartesian **representation where joint constraints are imposed numerically, causing **inaccuracies and instabilities** when elaborate kinematic structures are involved. MuJoCo was the first general-purpose engine to combine the best of both worlds: simulation in **generalized coordinates **and optimization-based contact dynamics. 


<a name="F8XVh"></a>
#### 2.4 数据格式
![image.png](assets/post_images/Simulation-Dynamics-Engine/image_010.png#clientId=u90167c2b-ba94-4&from=paste&height=738&id=u07132406&originHeight=1383&originWidth=1329&originalType=binary&ratio=1&rotation=0&showTitle=false&size=389307&status=done&style=none&taskId=u00bed35e-32c8-4026-a41b-d51436b2bf5&title=&width=708.8)
<a name="UZqER"></a>
#### 2.5 约束模型
<a name="XutCY"></a>
##### 2.5.1 等值约束
可以通过r(q)=0来建模等值约束，其中r是任意可微标量/向量函数,q是位置函数，r在语义上对应了残差(residual)，约束雅克比J中对应的块为∂r/∂q。注意由于四元数特性，∂r/∂q产生了nV维度的向量而不是nQ。<br />在其他应用如游戏引擎中，等值约束可以用于创建环关节(loop joints)，但是在MuJoCo中不推荐这样使用——因为这样会造成精度和求解效率下降。MuJoCo中唯一合理使用等值约束的地方是对不能采用运动链的柔性关节(soft joints)的建模。有五种等值约束类型和其constraint residual的维度。
<a name="hRd9e"></a>
##### 2.5.2 摩擦损失
摩擦损失(dry friction, static friction, load-independent friction)，为静摩擦力。跟阻尼或者粘滞力相似，其作用方向跟运动方向相反，不能建模为速度相关的力。因此这里定义其为约束，即静摩擦力幅值的上限。这个值可以在模型元素frictionloss中指定，可以施加在joint或者tendon上。<br />与其他约束类型不同，摩擦损失没有位置残差，因此我们设置r(q)=0。事实上为了整合进这个约束，我们的约束求解器需要进行扩展。另外受约束关节或者线缆的速度作为了速度“residual”，因为这个约束是为了尽量使速度趋于零，对应约束雅克比中的块为关节位置(或者线缆长度)对q的偏导:对应标量关节时one-hot向量，对应线缆时力臂向量。
<a name="S4JyT"></a>
##### 2.5.3 限位
限位是单边的空间残差约束，是不等值约束。限位可适用于关节(MJCF文件中limited)和线缆(range)。残差r(q)定义为当前值跟最大限制的距离。如果没有越过限制，则距离为正；反之为负。当此距离小于MJCF中定义的margin时，此约束被激活(不过并不意味着可以抵消margin的限制，设置margin为0。约束力是通过求解器中的[参数](https://link.zhihu.com/?target=http%3A//mujoco.org/book/computation.html%23soParameters)来定义的)。<br />有可能关节/线缆的上界和下界同事激活。此时它们都会被包含在标量约束集合中。但是这种情况不符合物理现实，需要手动增加限制范围或者修改margin值来避免。注意避免用小范围限制来近似等值约束，而是直接使用等值约束，通过调节求解器参数来保证约束的松弛度(这样能保证更高的计算效率，因为等值约束计算更快)。
<a name="mRYux"></a>
##### 2.5.4 接触
接触是最复杂的约束类型，因为接触建模的复杂性。MuJoCo可以支持通用的接触模型(切向、扭转滚动摩擦力)，支持椭圆摩擦锥和四面体摩擦锥。<br />MuJoCo接触采用点接触方法，几何上定义两个刚体间的接触点和固接在该点上的空间坐标系,均表达在全局坐标系中。坐标系的第一个轴(X轴)指向接触法向，另外两个轴(Y和Z)定义了切空间。定义法向轴为X轴的原因是为了让第一维度为法线方向，从而支持多种参数(比如可以没有Y、Z方向的摩擦力)。跟限位一样，当两个geom分离时为正、插入时为负。接触点在两个geom表面中间位置。

<a name="EspuD"></a>
#### 2.6 Unity插件
[https://mujoco.readthedocs.io/en/latest/unity.html](https://mujoco.readthedocs.io/en/latest/unity.html)<br />包括模型导入、仿真等功能，用Unity来渲染看结果。

<a name="d5ZPL"></a>
### 3 参考文献
[1] [Ivaldi, Serena, et al. "Tools for simulating humanoid robot dynamics: a survey based on user feedback." 2014 IEEE-RAS International Conference on Humanoid Robots. IEEE, 2014.](https://ieeexplore.ieee.org/document/7041462)<br />[2] [Chebotar, Yevgen, et al. "Closing the sim-to-real loop: Adapting simulation randomization with real world experience." 2019 International Conference on Robotics and Automation (ICRA). IEEE, 2019.](https://ieeexplore.ieee.org/abstract/document/8793789/)<br />[3] [Heiden, Eric, et al. "NeuralSim: Augmenting Differentiable Simulators with Neural Networks." arXiv preprint arXiv:2011.04217 (2020).](https://arxiv.org/abs/2011.04217)<br />[4] [UW CSE Robotics: Emo Todorov, "Goal-directed Dynamics"](https://www.youtube.com/watch%3Fv%3DANVW8jT52hc)<br />[5] [Todorov, Emanuel. "Convex and analytically-invertible dynamics with contacts and constraints: Theory and implementation in mujoco." 2014 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2014.](https://ieeexplore.ieee.org/abstract/document/6907751/)<br />[6] [Simulation Tools for Model-Based Robotics: Comparison of Bullet, Havok, MuJoCo, ODE and PhysX](https://homes.cs.washington.edu/~todorov/papers/ErezICRA15.pdf)
