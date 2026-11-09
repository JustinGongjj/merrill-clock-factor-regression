# Merrill Clock Factor Regression

**Author:** JustinGongjj · **License:** MIT

独立的因子回归与历史归因研究小项目：将策略收益与因子收益按日期对齐，按需扣除无风险收益，再用 OLS 估计因子载荷，并以 Newey–West/HAC 协方差估计标准误。它可以单独运行，不依赖 Merrill Clock Quant 仓库，也不包含信维通信研究或真实行情数据。

## 安装

需要 Python 3.10 或更新版本。

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[analysis,test]"
```

## 快速演示（离线）

```bash
python examples_factor_regression.py
```

默认使用固定随机种子的合成月收益，无网络请求，不代表任何实际策略。输出回归截距、因子系数、HAC t/p 值、样本数和 R-squared。

## 分析自己的收益

输入收益 CSV 至少需要 `date` 和 `net_return` 两列，收益率使用小数（例如 1% 写为 `0.01`）。若提供因子 CSV，它必须含有日期列及小数格式的因子收益；可选 `RF` 列作为无风险收益。

```bash
python examples_factor_regression.py \
  --returns-csv ./my_returns.csv \
  --factors-csv ./my_factors.csv \
  --return-column net_return \
  --date-column date \
  --maxlags 3
```

也可以不传 `--factors-csv`，脚本将运行时下载 Kenneth French Data Library 的美国月度五因子文件；请先查看当前数据定义和使用条款。数据适配器将源文件百分数转换为小数。此时需要联网。

Python API：

```python
from factorlab.regression import factor_regression

result = factor_regression(strategy_returns, factor_returns, maxlags=3, risk_free_returns=rf)
print(result.params)
print(result.tvalues)
```

## 测试

```bash
python -m pytest -q
```

测试使用合成数据，不访问网络。详见 [TESTING.md](TESTING.md)。

## 方法与限制

- 模型是线性 OLS。HAC/Newey–West 调整用于在指定最大滞后下估计对异方差及自相关稳健的协方差，不会修复错误数据、结构突变、遗漏因子或模型选择偏差。
- 截距是样本内历史回归截距，不等于未来 alpha，也不是因果效应；系数是样本条件下的统计关系。R-squared 不是收益质量或策略有效性的证明。
- 输入收益与因子收益应使用相同频率和相同单位，并考虑分红、费用、无风险利率定义及时间戳。因子回归只保留按日期成功对齐的完整观测。
- 默认演示样例是合成数据；没有捆绑策略业绩、真实因子数据或回归报告。提供的 Fama–French 下载器会在用户运行时请求第三方数据。
- 此项目仅供研究与教学，不构成投资建议、绩效保证或交易系统。

数据来源及授权提示见 [DATA_SOURCES.md](DATA_SOURCES.md)。MIT 许可仅适用于仓库内项目自有代码与文档，不扩展第三方数据权利。
