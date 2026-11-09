# 测试说明

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

测试使用内存生成的确定性月度因子和收益，不访问网络、不读取任何用户文件。覆盖风险无风险利率扣除后的 HAC 因子回归、合成离线演示和 CSV 日期/数值处理。
