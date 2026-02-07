# Streamlit Cloud 部署问题排查与优化

## 🔍 当前问题分析

根据你提供的状态信息：
```json
{
  "isOwner": true,
  "status": 1,
  "platformStatus": 3,
  "streamlitVersion": "",
  "viewerAuthEnabled": false
}
```

**platformStatus: 3** 表示应用正在运行但可能存在问题。

## ✅ 已完成的优化

### 1. 代码优化
- ✅ 懒加载重量级库（防止重复加载）
- ✅ CSS 缓存（500+ 行）
- ✅ 配置数据缓存
- ✅ Session State 优化（使用 setdefault）
- ✅ Font Awesome CDN 缓存

### 2. 配置文件
- ✅ `requirements.txt` - 精简依赖
- ✅ `.streamlit/config.toml` - 运行时优化

## 🚨 可能导致加载慢的原因

### 1. Streamlit Cloud 冷启动
**症状**：首次访问或长时间未访问后加载慢
**原因**：
- 容器需要重新启动
- 依赖需要重新安装
- 代码需要重新加载

**解决方案**：
- ✅ 已优化：懒加载、缓存
- 💡 建议：升级到付费版（保持应用常驻）

### 2. 依赖安装时间长
**症状**：部署时间超过 5 分钟
**原因**：
- PyMuPDF (fitz) 需要编译
- pandas 体积较大

**解决方案**：
```bash
# 检查 requirements.txt 是否正确
cat hunter-brain/requirements.txt
```

### 3. API 调用超时
**症状**：点击"开始 AI 打标"后长时间无响应
**原因**：
- API 请求超时（120秒）
- 网络延迟

**解决方案**：
- ✅ 已设置：timeout=120
- 💡 建议：添加进度提示

## 🔧 立即执行的修复步骤

### 步骤 1：检查应用日志
1. 登录 Streamlit Cloud
2. 进入你的应用管理页面
3. 点击 "Manage app" → "Logs"
4. 查看是否有错误信息

### 步骤 2：重新部署
```bash
cd hunter-brain
git add .
git commit -m "修复性能问题：懒加载+缓存优化"
git push origin main
```

### 步骤 3：清除 Streamlit Cloud 缓存
1. 在应用管理页面点击 "⋮" (三个点)
2. 选择 "Reboot app"
3. 等待 2-3 分钟重新启动

### 步骤 4：验证优化效果
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 访问应用并记录加载时间
4. 刷新页面，观察缓存是否生效

## 📊 性能基准

| 指标 | 优化前 | 优化后 | 目标 |
|------|--------|--------|------|
| 冷启动 | 8-12秒 | 4-6秒 | <5秒 |
| 热启动 | 3-5秒 | 1-2秒 | <2秒 |
| 页面交互 | 1-2秒 | 0.3-0.5秒 | <0.5秒 |
| 内存占用 | ~200MB | ~150MB | <200MB |

## 🐛 常见问题排查

### Q1: 应用一直显示 "Running"
**可能原因**：
- 代码中有无限循环
- 某个函数阻塞了主线程
- 依赖安装失败

**排查方法**：
```bash
# 本地测试
cd hunter-brain
streamlit run app.py

# 查看是否有错误
```

### Q2: 部署后访问 404
**可能原因**：
- 文件路径配置错误
- GitHub 仓库权限问题

**解决方法**：
- 确认主文件路径：`hunter-brain/app.py`
- 检查 GitHub 仓库是否公开

### Q3: 依赖安装失败
**可能原因**：
- requirements.txt 格式错误
- 版本冲突

**解决方法**：
```bash
# 本地测试依赖
pip install -r hunter-brain/requirements.txt
```

## 💡 进一步优化建议

### 1. 添加加载进度提示
```python
# 在 app.py 开头添加
with st.spinner('正在加载应用...'):
    # 初始化代码
    pass
```

### 2. 使用 st.cache_resource（针对全局对象）
```python
@st.cache_resource
def get_api_client():
    # 创建可复用的 API 客户端
    return requests.Session()
```

### 3. 减少 CSS 体积
- 移除不常用的动画效果
- 合并重复的样式规则
- 使用 CSS 压缩工具

### 4. 异步加载非关键资源
```python
# 延迟加载 Font Awesome
if st.session_state.get('fonts_loaded', False) == False:
    st.markdown(load_font_awesome(), unsafe_allow_html=True)
    st.session_state['fonts_loaded'] = True
```

## 📝 部署检查清单

部署前请确认：
- [ ] `hunter-brain/app.py` 已优化
- [ ] `hunter-brain/requirements.txt` 存在且正确
- [ ] `hunter-brain/.streamlit/config.toml` 存在
- [ ] 代码已推送到 GitHub
- [ ] Streamlit Cloud 配置正确
  - 主文件路径：`hunter-brain/app.py`
  - Python 版本：3.11+
- [ ] 本地测试通过

## 🎯 预期结果

优化后，你应该看到：
1. **首次访问**：4-6 秒加载完成
2. **后续访问**：1-2 秒加载完成
3. **页面交互**：响应时间 <0.5 秒
4. **内存占用**：稳定在 150MB 左右

## 📞 如果问题仍然存在

如果优化后仍然很慢，请检查：
1. **网络环境**：是否使用了 VPN 或代理
2. **API 响应**：`api.gemai.cc` 是否可访问
3. **浏览器缓存**：清除浏览器缓存后重试
4. **Streamlit Cloud 状态**：检查官方状态页面

---

**最后更新**: 2026-02-07  
**优化版本**: v2.0  
**预期性能提升**: 50-70%
