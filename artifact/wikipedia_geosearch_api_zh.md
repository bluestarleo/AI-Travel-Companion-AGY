# 维基百科地理位置搜索 (Geosearch) API 文档

维基百科地理位置搜索 API (Geosearch API) 允许您检索指定地理坐标附近的维基百科文章或兴趣点 (POI)。通过使用该 API 的 **生成器 (generator)** 功能，您可以在单次 HTTP 请求中同时获取页面详情、坐标、简短摘要以及代表性图片。

---

## 1. API 端点与核心参数

* **基础 URL (Base URL)**: `https://en.wikipedia.org/w/api.php`
* **返回格式**: 所有的请求都应该包含 `format=json`，以便以 JSON 格式返回数据。

### 地理搜索参数

无论使用 `list=geosearch` (仅返回页面 ID/标题) 还是 `generator=geosearch` (通过属性返回页面详细信息)，都可以使用以下参数来过滤结果：

| 参数 | 类型 | 是否必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `gscoord` / `ggscoord` | 字符串 | **是** | 搜索的中心坐标，格式为 `纬度\|经度` (例如 `48.8584\|2.2945`)。 |
| `gsradius` / `ggsradius` | 整数 | **是** | 搜索半径 (以米为单位)。最大值为 `10000` (10 公里)。 |
| `gslimit` / `ggslimit` | 整数 | 否 | 每次返回的最大结果数。默认为 `10`，最大值为 `500`。 |

> [!NOTE]
> 当使用 `generator=geosearch` 时，所有地理搜索相关的参数必须以 `ggs` 开头 (例如 `ggscoord`、`ggsradius`、`ggslimit`)，以此与标准的 API 参数进行区分。

---

## 2. 高级用法：获取丰富的页面数据

要获取包含摘要和照片的兴趣点，请将 `geosearch` 生成器与页面属性联合使用：

```http
GET https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=5&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json
```

### 关键属性参数
* `prop=coordinates|pageimages|extracts`: 返回坐标、缩略图信息和页面文本摘要。
* `pithumbsize=250`: 指定图片缩略图的宽度像素值 (获取 `thumbnail.source` 直链 URL 所必需)。
* `exintro=1` 和 `explaintext=1`: 将页面内容限制在引言部分，并去除 HTML 标签 (仅返回纯文本)。

---

## 3. 如何进行测试 (cURL & PowerShell)

### 使用 cURL
```bash
curl -s "https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=3&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json"
```

### 使用 PowerShell
```powershell
$uri = "https://en.wikipedia.org/w/api.php?action=query&generator=geosearch&ggscoord=48.8584|2.2945&ggsradius=1000&ggslimit=3&prop=coordinates|pageimages|extracts&pithumbsize=250&exintro=1&explaintext=1&format=json"
Invoke-RestMethod -Uri $uri -Method Get
```

---

## 4. 在线 API 测试运行结果

以下是通过在 **埃菲尔铁塔 (48.8584, 2.2945)** 附近运行 **1000米** 半径的搜索所得出的在线真实结果：

<!-- LIVE_RESULTS_START -->
### 埃菲尔铁塔 (Eiffel Tower)
- **坐标**: (48.85822222, 2.2945)
![Eiffel Tower](https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/250px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg)
- **摘要**: 埃菲尔铁塔 (Eiffel Tower，法语: Tour Eiffel) 是位于法国巴黎战神广场的铁制镂空塔。它以设计并建造它的工程师居斯塔夫·埃菲尔的名字命名，由其公司于1887年至1889年建造。
当地人因其采用锻铁建造而昵称其为“铁娘子”(Iron Lady)。

---

### 耶拿桥 (Pont d'Iéna)
- **坐标**: (48.85972222, 2.29222222)
- **摘要**: 耶拿桥 (Pont d'Iéna) 是横跨法国巴黎塞纳河的一座桥梁。它将左岸的埃菲尔铁塔与右岸的夏乐宫/托卡德罗地区连接起来。

---

### 天体仪 (Globe Céleste)
- **坐标**: (48.8575, 2.29277778)
![Globe Céleste](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Tour_Eiffel_et_le_Globe_C%C3%A9leste.jpg/250px-Tour_Eiffel_et_le_Globe_C%C3%A9leste.jpg)
- **摘要**: 天体仪 (Globe Céleste) 是1900年巴黎世界博览会的标志性建筑，类似于埃菲尔铁塔。它被建造为一个巨大的地球仪形状，紧邻埃菲尔铁塔。这是一个直径45米的蓝金相间球体，上面绘制了星座和黄道十二宫。

---

### 巴黎美国图书馆 (American Library in Paris)
- **坐标**: (48.8589, 2.299)
- **摘要**: 巴黎美国图书馆是欧洲大陆最大的英语借阅图书馆。它作为法国的一个独立非营利文化协会运营，根据特拉华州法律成立。图书馆会员可以访问超过10万册书籍和期刊。

---

### 贝纳多·纳尼·卢切斯宫 (Palazzo Bernardo Nani)
- **坐标**: (48.8583, 2.2923)
![Palazzo Bernardo Nani](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Palazzo_bernardo_nani_gran_canal_dorsoduro.jpg/250px-Palazzo_bernardo_nani_gran_canal_dorsoduro.jpg)
- **摘要**: 贝纳多·纳尼·卢切斯宫 (Palazzo Bernardo Nani Lucheschi)，也称为纳尼贝纳多宫，是位于意大利威尼斯多尔索杜罗区大运河畔的一座文艺复兴风格宫殿，介于贝纳多朱斯蒂尼安宫与更大更宏伟的雷佐尼科宫之间。

---
<!-- LIVE_RESULTS_END -->
