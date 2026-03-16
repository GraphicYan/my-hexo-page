---
title: 生成式模型数学原理与 3D 生成分类全景
layout: 3D-Generation-Basic
toc: true
tag: 3D Reconstruction
date: 2026/01/21 19:56:45
---

> **来源**：综合 [周弈帆博客](https://zhouyifan.net/2022/12/19/20221016-VAE/)、知乎专栏、arXiv 论文、Web 调研
> **原始格式**：笔记
> **收录日期**：2026-03-12
> **标签**：[VAE, Diffusion, Flow Matching, Rectified Flow, U-Net, Transformer, DiT, 3D生成, 数学原理, 生成模型]

---

## 第一部分：三大生成式模型数学原理

### 一、VAE（变分自编码器）

#### 1.1 核心思想——一句话版

> **VAE = 自编码器 + 概率正则化**。编码器把数据压缩为一个**分布**（而非单点），解码器从分布中采样重建数据。

#### 1.2 为什么需要 VAE？

普通自编码器（AE）可以做信息压缩，但存在严重的**过拟合**问题：编码器可以把所有训练图片映射为简单序号（0, 1, 2...），解码器再查表还原。这种极端压缩使得**编码失去语义连续性**——序号 1.5 没有意义，不能生成"介于 1 号和 2 号之间"的图片。

VAE 的解决方案：**让每张图片编码为一个正态分布，而非一个点**。多个重叠的分布自然拼成一条连续的概率曲线，解码器学会从曲线上的任意位置生成合理图片。

#### 1.3 数学框架

**模型结构**：
```
输入 x → 编码器 → (μ, σ²) → 重参数化采样 z = μ + σ·ε (ε~N(0,I)) → 解码器 → x̂
```

**损失函数**由两项组成：

$$\mathcal{L}_{VAE} = \underbrace{\| x - \hat{x} \|^2}_{\text{重建损失}} + \underbrace{\lambda \cdot D_{KL}\big(q_\phi(z|x) \,\|\, \mathcal{N}(0, I)\big)}_{\text{KL 正则}}$$

| 项 | 直觉 | 数学含义 |
|----|------|----------|
| 重建损失 | 解码后的图片应尽量像原图 | 最大化 \(p_\theta(x \| z)\) |
| KL 正则 | 编码出的分布不能太"奇怪"，要接近标准正态 | 限制隐空间不过拟合 |

**KL 散度的解析公式**（两个正态分布之间）：

$$D_{KL} = -\frac{1}{2}\sum_{j=1}^{d}\left(1 + \log\sigma_j^2 - \mu_j^2 - \sigma_j^2\right)$$

这个公式可以直接计算，不需要采样估计。

**重参数化技巧**：采样操作 \(z \sim \mathcal{N}(\mu, \sigma^2)\) 不可微，但可以改写为 \(z = \mu + \sigma \cdot \epsilon\)（其中 \(\epsilon \sim \mathcal{N}(0,I)\)），使梯度能穿过采样操作回传到编码器。

#### 1.4 变分推理视角（简述）

VAE 的损失函数并非凭空设计，而是从**变分推理**严格推导而来：

1. 我们想最大化数据的对数似然 \(\log p_\theta(x)\)
2. 直接求解需要积分 \(\int p_\theta(x|z)p(z)dz\)，通常不可解
3. 引入近似后验 \(q_\phi(z|x)\)（编码器），利用 **ELBO（证据下界）** 把不可解的积分转化为可优化的损失
4. 最大化 ELBO 等价于最小化上面的 VAE 损失

$$\log p(x) \geq \underbrace{\mathbb{E}_{q(z|x)}[\log p(x|z)]}_{\text{重建}} - \underbrace{D_{KL}(q(z|x) \| p(z))}_{\text{正则}} = \text{ELBO}$$

#### 1.5 VAE 的特点

| 优点 | 缺点 |
|------|------|
| 训练稳定，不会模式崩塌 | 生成图像偏模糊（MSE 损失倾向均值） |
| 有显式隐空间，支持插值/编辑 | 隐空间分布假设限制表达力 |
| 一次前向即可生成（快） | 独立使用效果不如 GAN/Diffusion |
| 可做密度估计 | KL 权重需要仔细调节 |

---

### 二、Diffusion Model（扩散模型 / DDPM）

#### 2.1 核心思想——一句话版

> **扩散模型 = 逐步加噪 + 学会去噪**。把数据慢慢变成纯噪声（前向过程），然后训练网络学会反向操作（去噪过程），从纯噪声逐步还原数据。

#### 2.2 前向过程（加噪）

从干净数据 \(x_0\) 出发，逐步添加高斯噪声，经过 T 步变成纯噪声 \(x_T \sim \mathcal{N}(0, I)\)：

$$q(x_t | x_{t-1}) = \mathcal{N}\big(x_t; \sqrt{1-\beta_t}\, x_{t-1},\; \beta_t I\big)$$

其中 \(\beta_t\) 是**噪声调度**（noise schedule），控制每步加多少噪声。

**关键性质：可以跳步**。不需要逐步模拟，可以直接从 \(x_0\) 跳到任意 \(x_t\)：

$$x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1-\bar{\alpha}_t}\, \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

其中 \(\bar{\alpha}_t = \prod_{s=1}^{t}(1-\beta_s)\)。这使得训练非常高效。

#### 2.3 反向过程（去噪）

学习一个神经网络 \(\epsilon_\theta(x_t, t)\) 来预测加入的噪声，从而逐步去噪：

$$p_\theta(x_{t-1} | x_t) = \mathcal{N}\big(x_{t-1}; \mu_\theta(x_t, t),\; \sigma_t^2 I\big)$$

通过预测的噪声 \(\epsilon_\theta\) 计算均值 \(\mu_\theta\)，每步都"减去一点噪声"，T 步后回到干净数据。

#### 2.4 训练目标

从 ELBO 推导可以证明，优化目标等价于一个**极其简单的 MSE 损失**：

$$\mathcal{L}_{simple} = \mathbb{E}_{t, x_0, \epsilon}\left[\| \epsilon - \epsilon_\theta(x_t, t) \|^2\right]$$

**直觉**：随机选一个时间步 t，给 \(x_0\) 加噪声得到 \(x_t\)，让网络预测加了什么噪声。预测越准，去噪越好。

#### 2.5 Score Matching 视角

扩散模型还有一个等价的理解方式——**得分匹配**（Score Matching）：

- **得分函数**：\(\nabla_x \log p(x)\)，指向数据分布高概率区域的梯度
- 扩散模型实际上在学习**带噪声的得分函数**
- 去噪过程等价于**朗之万动力学**（Langevin dynamics）：沿得分方向"爬坡"

两种视角的关系：\(\epsilon_\theta(x_t, t) \approx -\sqrt{1-\bar{\alpha}_t} \cdot \nabla_{x_t} \log p(x_t)\)

#### 2.6 Diffusion 的特点

| 优点 | 缺点 |
|------|------|
| 生成质量极高（SOTA 级别） | 推理慢（需要多步去噪，20-1000步） |
| 训练稳定，损失简洁 | 计算成本高 |
| 支持条件生成（CFG） | 前向过程固定为加高斯噪声 |
| 理论基础扎实（SDE/Score） | 只能从高斯先验开始 |

---

### 三、Flow Matching（流匹配 / Rectified Flow）

#### 3.1 核心思想——一句话版

> **Flow Matching = 学习一个速度场，让噪声沿最短路径"流动"到数据**。不加噪、不去噪，直接学"从哪到哪走多快"。

#### 3.2 物理直觉

想象一个水池：一端放入墨水（噪声分布），另一端是目标形状（数据分布）。Flow Matching 学习的就是**流速场**——池中每个位置、每个时刻的水流方向和速度。沿着流线走，墨水就变成目标形状。

**关键约束**：流线不能交叉。这保证了变换是可逆的，每个噪声点唯一对应一个数据点。

#### 3.3 数学框架

定义一个**常微分方程（ODE）**：

$$\frac{d\psi_t(x)}{dt} = v_t\big(\psi_t(x)\big), \quad t \in [0, 1]$$

其中 \(v_t\) 是要学习的速度场，\(\psi_0(x) = x\)（初始位置），\(\psi_1(x)\) 是最终位置。

- \(t=0\) 时：样本来自噪声分布 \(p_0 = \mathcal{N}(0, I)\)
- \(t=1\) 时：样本到达数据分布 \(p_1 = p_{data}\)

#### 3.4 训练方法——条件流匹配

直接学习全局速度场很难，但有一个巧妙的简化：**条件流匹配**（Conditional Flow Matching）。

1. **配对**：随机取一个噪声点 \(x_0 \sim \mathcal{N}(0,I)\) 和一个数据点 \(x_1 \sim p_{data}\)
2. **线性插值**：假设它们之间的路径是直线：\(x_t = (1-t) x_0 + t \cdot x_1\)
3. **目标速度**：直线路径的速度恒为 \(v^* = x_1 - x_0\)
4. **训练**：让网络预测这个速度

$$\mathcal{L}_{FM} = \mathbb{E}_{t, x_0, x_1}\left[\| v_\theta(x_t, t) - (x_1 - x_0) \|^2\right]$$

这个损失和扩散模型的 \(\epsilon\)-prediction 惊人地相似！

#### 3.5 Rectified Flow（整流流）

**Rectified Flow** 是 Flow Matching 的一种改进，核心思想是让路径**尽量笔直**：

- 弯曲的路径 → 需要更多步数才能准确积分
- 笔直的路径 → 极少步甚至 1 步就能完成

通过**Reflow**操作（多次训练让路径越来越直），可以逐步减少采样步数。TripoSG 和 Stable Diffusion 3 都使用这一技术。

#### 3.6 与 Diffusion 的深层联系

Flow Matching 和 Diffusion 并非完全独立：

| 维度 | Diffusion | Flow Matching |
|------|-----------|---------------|
| 数学工具 | SDE（随机微分方程） | ODE（常微分方程） |
| 路径类型 | 随机游走（弯曲、有噪声） | 确定性流（可以很直） |
| 训练目标 | 预测噪声 \(\epsilon\) | 预测速度 \(v = x_1 - x_0\) |
| 先验限制 | 必须是高斯噪声 | 可以是任意分布 |
| 采样效率 | 路径弯曲度~3.45 | 路径弯曲度~1.02 |
| 最少步数 | ~20步（DDIM）才不崩溃 | ~10步保持质量 |

**等价性**：在特定参数设置下，Diffusion 的 DDIM 采样器就是一个 ODE solver，与 Flow Matching 等价。

#### 3.7 Flow Matching 的特点

| 优点 | 缺点 |
|------|------|
| 路径直→采样步数少→推理快 | 相对较新，生态不如 Diffusion |
| 训练简洁，不需要噪声调度 | 确定性路径缺少多样性（需要后处理） |
| 支持任意分布变换 | 大规模训练的工程经验积累少 |
| 与最优传输理论自然连接 | 数据量少时稳定性不如 Diffusion Bridge |

---

### 四、三大模型的统一视角

这三种模型其实可以用一个统一框架理解——**如何把简单分布变成复杂分布**：

```
         简单分布 p(z)                复杂分布 p(x)
       (标准高斯噪声)                 (真实数据)
              │                           │
   VAE:       │── 解码器直接映射 ──────────→│   (一步，但模糊)
              │                           │
   Diffusion: │── 逐步去噪(SDE) ─────────→│   (多步，高质量)
              │                           │
   Flow:      │── 沿速度场流动(ODE) ──────→│   (少步，高效)
```

| 维度 | VAE | Diffusion | Flow Matching |
|------|-----|-----------|---------------|
| 核心数学 | 变分推理 + KL散度 | SDE + Score Matching | ODE + 最优传输 |
| 训练损失 | 重建 + KL正则 | 噪声预测 MSE | 速度预测 MSE |
| 生成步数 | 1 步 | 20-1000 步 | 1-50 步 |
| 隐空间 | 显式、可解释 | 隐含在去噪过程中 | 隐含在流动路径中 |
| 生成质量 | 中等 | 高 | 高 |
| 推理速度 | 最快 | 最慢 | 中等偏快 |
| 典型用途 | 信息压缩、隐空间编辑 | 高质量图像/3D生成 | 高效图像/3D生成 |

---

## 第二部分：U-Net 与 Transformer 的作用

### 五、为什么生成模型需要骨干网络？

VAE/Diffusion/Flow Matching 定义了**"学什么"**（重建、去噪、预测速度），但没有规定**"用什么网络来学"**。骨干网络（backbone）就是那个做实际计算的神经网络。

### 六、U-Net——扩散模型的经典骨干

#### 6.1 结构

```
输入(带噪图) ──→ 下采样(编码) ──→ 中间层 ──→ 上采样(解码) ──→ 输出(噪声预测)
                    │                                │
                    └───────── Skip Connection ──────┘
```

- **下采样路径**：逐步降低分辨率、增加通道数，捕获**全局语义**
- **上采样路径**：逐步恢复分辨率，重建**局部细节**
- **Skip Connection**：将下采样的高分辨率特征跳接到上采样对应层，保留细节

#### 6.2 为什么适合生成模型

- **多尺度处理**：同时理解全局结构和局部纹理
- **参数效率**：通过下采样减少计算量
- **条件注入**：时间步 t 通过 AdaGN/FiLM 注入各层，图像条件通过 Cross-Attention 注入
- **输出与输入同尺寸**：天然适合"输入噪声图→输出噪声/速度预测"

#### 6.3 局限

- **归纳偏置强**：卷积的局部感受野限制全局建模
- **扩展性差**：增大 U-Net 的收益边际递减，不遵循 Scaling Law
- **不灵活**：难以处理非图像结构的数据（点云、稀疏体素）

---

### 七、Transformer（DiT）——生成模型的新骨干

#### 7.1 DiT（Diffusion Transformer）核心设计

Sora 的基础模型。核心改变：**用 Transformer 块替换 U-Net 中的卷积块**。

```
输入 patch tokens ──→ [DiT Block × N] ──→ 输出 noise/velocity 预测
每个 DiT Block: LayerNorm → Self-Attention → LayerNorm → FFN
时间步 t: 通过 AdaLN（自适应层归一化）注入
```

- 图像先被**切成 patch**（如 2×2），展平为 token 序列
- 每个 token 通过 Self-Attention 与所有其他 token 交互
- 时间步条件通过 AdaLN-Zero 注入

#### 7.2 为什么转向 Transformer

| 维度 | U-Net | DiT (Transformer) |
|------|-------|-------------------|
| 感受野 | 局部（卷积核大小） | 全局（Self-Attention） |
| Scaling Law | ❌ 不遵循 | ✅ 遵循（性能随参数量对数增长） |
| 多模态 | 困难 | 容易（统一 token 接口） |
| 条件注入 | Cross-Attention 或 FiLM | Cross-Attention + AdaLN |
| 3D 数据适配 | 需要 3D 卷积 | token 化后通用 |

**Scaling Law 是关键**：DiT 论文证明了扩散模型也遵循 Scaling Law——更大的 Transformer + 更多数据 = 更好的效果。这是 U-Net 做不到的。

#### 7.3 U-DiT：融合两者优势

北大 & 华为（NeurIPS 2024）提出 U-DiT：在 U-Net 框架内使用 Transformer 块，并对 Self-Attention 做 Token 下采样。结果：**1/6 算力超越 DiT-XL**。

原理：U-Net 的特征主要为低频信号，下采样自然滤除高频冗余，让 Attention 更高效。

#### 7.4 在 3D 生成中的应用

| 系统 | 骨干 | 处理对象 | 条件注入 |
|------|------|----------|----------|
| TripoSG | DiT + U-Net Skip | VecSet tokens [2048×64] | DINOv2 Cross-Attention |
| TRELLIS | Sparse DiT | 稀疏体素 tokens | DINOv2 + 多视图 |
| SparseFlex | Swin Transformer | 稀疏体素 SparseTensor | — (VAE 内部) |
| Hunyuan3D | DiT | 多视图特征 | CLIP + DINOv2 |
| MeshGPT | GPT-style Transformer | 面坐标 tokens | — (自回归) |
| FACE | Encoder-Decoder Transformer | 面级 latent tokens | VecSet Encoder |

**Transformer 在 3D 中的关键作用**：
1. **Self-Attention**：捕获 3D 空间的全局关系（远距离顶点交互）
2. **Cross-Attention**：注入 2D 图像条件（DINOv2/CLIP 特征）
3. **Token 化**：将不同 3D 表示（体素、点云、面）统一为序列

---

## 第三部分：3D 生成方法按数学模型分类

### 八、分类框架

按**底层生成式数学模型**对当前 3D 生成方法分类：

#### A 类：纯自回归（Autoregressive / AR）

> 数学基础：链式分解 \(p(x) = \prod_i p(x_i | x_{<i})\)，逐 token 预测

| 方法 | 时间 | 3D 表示 | 骨干 | 关键特点 |
|------|------|---------|------|----------|
| MeshGPT | 2024.02 | 面坐标 tokens | GPT Transformer | 首个端到端 AR mesh 生成 |
| MeshAnything V2 | 2025.08 | AMT 压缩 tokens | GPT Transformer | 邻接压缩 2×，1600 面 |
| MeshWeaver | 2026 ICLR | 稀疏体素引导 tokens | Transformer + 体素 Cross-Attn | 18% 压缩比，16K 面 |
| DeepMesh | 2025.03 | 坐标 tokens | GPT-2 style | 几何 + 拓扑 tokens |
| HiFi-Mesh | 2026.01 | LANE latent tokens | AR + 自适应计算图 | 6× 序列长度提升 |

**特点**：
- ✅ 直接输出干净拓扑 Mesh
- ✅ 可控性好（可逐步编辑）
- ❌ 推理速度慢（逐 token 生成，O(N²) 注意力）
- ❌ 序列过长（一个 8000 面网格 = 24000+ tokens）
- ❌ 因果偏置导致全局一致性差

#### B 类：Diffusion / Score-based

> 数学基础：SDE 前向加噪 + Score Matching 反向去噪

| 方法 | 时间 | 3D 表示 | 骨干 | 关键特点 |
|------|------|---------|------|----------|
| Hunyuan3D 2.0 | 2025.01 | 多视图→SDF/Mesh | DiT | 腾讯，双阶段Diffusion |
| Rodin Gen-2 | 2025 | 三平面NeRF latent | BANG arch | Deemos，~15s |
| Direct3D-S2 | 2025 | 稀疏体素 | DiT | DreamTech，扩散+稀疏 |
| PartDiffuser | 2025.11 | 部件级面片 | Discrete Diffusion | 半AR + 并行扩散 |

**特点**：
- ✅ 全局一致性好（并行去噪）
- ✅ 质量高（Score Matching 理论保证）
- ✅ 支持 CFG 条件引导
- ❌ 推理步数多（20-100步）
- ❌ 只能从高斯先验出发

#### C 类：Flow Matching / Rectified Flow

> 数学基础：ODE 速度场 + 条件流匹配

| 方法 | 时间 | 3D 表示 | 骨干 | 关键特点 |
|------|------|---------|------|----------|
| TripoSG | 2025.02 | VecSet SDF | DiT + U-Net Skip | VAST，1.5B，50 步 |
| TRELLIS 1.0 | 2024.12 | SLAT 稀疏体素 | Sparse DiT | Microsoft，RF + 结构化 latent |
| TRELLIS 2.0 | 2025 | O-Voxel 稀疏体素 | 4B Sparse DiT | ~3s@512³，1536³ |
| LATO | 2026.03 | VDF + 稀疏体素 | Flow Matching | **两阶段 FM**，拓扑保持 |
| **Tripo P1.0** | 2026 | SparseFlex | 两阶段 RF DiT | **2 秒**，引擎级拓扑 |
| Step1X-3D | 2025 | 多视图→3D | Flow Matching | StepFun，多视图路线 |

**特点**：
- ✅ 路径直→步数少→推理快
- ✅ 与 RF 蒸馏兼容→极少步推理
- ✅ 全局并行，无因果偏置
- ✅ 支持多种先验分布
- ❌ 对训练数据分布敏感
- ❌ 确定性路径多样性稍弱

#### D 类：VAE + 扩散/流匹配 混合

> 数学基础：VAE 做隐空间压缩 + Diffusion/FM 在隐空间生成

| 方法 | 时间 | VAE 部分 | 生成部分 | 关键特点 |
|------|------|----------|----------|----------|
| SparseFlex | 2025.03 | 稀疏体素 VAE | (需配合生成模型) | VAST，1024³，FlexiCubes |
| FACE | 2026.03 | VecSet ARAE | Latent Diffusion | 面级压缩 0.11 |
| EdgeRunner | 2024.09 | EdgeBreaker VAE | Latent Diffusion | 50% 压缩 |
| Latent Diffusion 3D | 多种 | TriplaneVAE | DiT Diffusion | 经典范式 |
| **Tripo P1.0** | 2026 | SparseFlex VAE | 两阶段 RF | 混合：VAE 表示 + FM 生成 |

**特点**：
- ✅ VAE 大幅压缩 3D 表示→降低生成计算量
- ✅ 隐空间平滑→生成质量高
- ✅ 可复用预训练 VAE
- ❌ VAE 压缩带来信息损失
- ❌ 两步训练（先 VAE 后生成器）增加工程复杂度

#### E 类：GAN / 前馈（Feed-forward）

> 数学基础：对抗训练 / 直接回归

| 方法 | 时间 | 核心 | 关键特点 |
|------|------|------|----------|
| TripoSR | 2024.03 | LRM 前馈 | 0.5s 单图到 3D，质量有限 |
| InstantMesh | 2024 | LRM + 多视图 | 前馈重建 |

**特点**：
- ✅ 极快（单次前向）
- ❌ 质量上限低
- ❌ 缺乏多样性

---

### 九、综合对比表

| 维度 | AR | Diffusion | Flow Matching | VAE+FM 混合 | 前馈 |
|------|-----|-----------|---------------|-------------|------|
| **数学基础** | 链式分解 | SDE+Score | ODE+速度场 | 变分推理+ODE | 直接回归 |
| **生成速度** | 慢(10s-min) | 中(5-30s) | 快(2-5s) | 快(2-5s) | 极快(<1s) |
| **拓扑质量** | ★★★★★ | ★★★ | ★★★★ | ★★★★★ | ★★ |
| **几何精度** | ★★★★ | ★★★★ | ★★★★ | ★★★★★ | ★★★ |
| **全局一致** | ★★ | ★★★★ | ★★★★★ | ★★★★★ | ★★★ |
| **可扩展性** | ★★★ | ★★★★ | ★★★★★ | ★★★★★ | ★★ |
| **代表系统** | MeshGPT | Hunyuan3D | TripoSG/TRELLIS | **Tripo P1.0** | TripoSR |
| **2026趋势** | 压缩提速 | 被FM取代 | 主流方向 | **最优路线** | 辅助角色 |

### 十、趋势判断

**2025-2026 的明确趋势**：

1. **Flow Matching 正在取代 Diffusion** 成为 3D 生成的主流生成框架
   - TripoSG、TRELLIS 1.0/2.0、Tripo P1.0 全部使用 Rectified Flow
   - 路径更直 → 更少步数 → 更快推理

2. **VAE + Flow Matching 的混合范式** 是当前最优路线
   - VAE 负责 3D 表示压缩（SparseFlex 稀疏体素）
   - FM 在压缩后的 latent 空间做高效生成
   - 解码器直接输出干净 Mesh（FlexiCubes）

3. **Transformer 正在全面替代 U-Net** 作为骨干网络
   - 遵循 Scaling Law → 更大模型 = 更好效果
   - 稀疏 Transformer 适配 3D 稀疏数据结构

4. **蒸馏技术（MDT-dist 等）** 是实现 2 秒生成的关键
   - 教师模型训好后，蒸馏到 1-2 步推理
   - 与 Flow Matching 的直路径天然兼容