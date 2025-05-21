# CoinW API 文档

## 目录
1. [介绍](#介绍)
2. [认证与签名](#认证与签名)
3. [USDT保证金合约API](#usdt保证金合约api)
   - [查询未完成订单](#查询未完成订单)
   - [查询待处理订单数量](#查询待处理订单数量)
   - [查询个人交易历史](#查询个人交易历史)
   - [查询产品信息](#查询产品信息)
   - [查看永续合约当前资金费率](#查看永续合约当前资金费率)
   - [查看系统时间](#查看系统时间)
   - [查看衍生品仓位档位](#查看衍生品仓位档位)
   - [张币转换](#张币转换)
   - [查看持仓信息](#查看持仓信息)
   - [查询全部持仓](#查询全部持仓)
   - [查看历史持仓信息](#查看历史持仓信息)
   - [设置持仓模式](#设置持仓模式)
   - [查看仓位模式](#查看仓位模式)
   - [查看最大可买卖/开仓数量](#查看最大可买卖开仓数量)
   - [查看最大可用数量](#查看最大可用数量)
   - [查看账户最大可转余额](#查看账户最大可转余额)
   - [调整保证金](#调整保证金)
   - [查看杠杆倍数](#查看杠杆倍数)
   - [当前账户的手续费率](#当前账户的手续费率)
   - [下单](#下单)
   - [批量下单](#批量下单)
   - [批量平仓](#批量平仓)
   - [撤单](#撤单)
   - [批量撤单](#批量撤单)
   - [修改订单](#修改订单)
   - [平仓](#平仓)
   - [市价仓位全平](#市价仓位全平)
   - [一键反向](#一键反向)
   - [获取订单信息](#获取订单信息)
   - [查看历史订单记录](#查看历史订单记录)
   - [查看成交明细](#查看成交明细)
   - [查看仓位保证金率](#查看仓位保证金率)
   - [查看止盈止损信息](#查看止盈止损信息)
   - [设置止盈止损](#设置止盈止损)
   - [添加分批止盈止损](#添加分批止盈止损)
   - [修改分批止盈止损](#修改分批止盈止损)
   - [查看移动止盈止损信息](#查看移动止盈止损信息)
   - [设置移动止盈止损](#设置移动止盈止损)
   - [查看合约万能金信息](#查看合约万能金信息)
   - [设置合约万能金状态](#设置合约万能金状态)
   - [获取用户资产信息](#获取用户资产信息)
   - [查看所有币对行情信息](#查看所有币对行情信息)
4. [WebSocket API](#websocket-api)
   - [K线](#k线)
   - [订单薄](#订单薄)
   - [成交历史](#成交历史)
   - [资产及订单](#资产及订单)
   - [订阅订单](#订阅订单)
   - [订阅资产](#订阅资产)

## 介绍

这是CoinW交易所的官方API文档，将持续更新，请关注最新更新。

您可以在顶部菜单中切换不同的API业务，并通过点击右上角的按钮切换不同的语言。

文档右侧是请求参数和响应结果的示例。

## 认证与签名

### 1. 获取Access Key和Secret Key

Access Key和Secret Key可以通过创建API Key获取。Access Key用于API访问，Secret Key作为私钥用于请求参数签名。注意！为了您的账户安全，请勿向任何人透露您的密钥。

### 2. 生成未签名字符串

#### HTTP Header

| 参数 | 值 |
| --- | --- |
| timestamp | 时间戳 |
| api_key | Access Key |
| sign | 加密参数 |

签名(sign)使用base64 + HMAC SHA256算法。使用"secret_key"作为HMAC SHA256的密钥。将所有其他参数作为操作数应用后，获取输出结果，然后进行base64编码。

#### GET请求示例

```
GET /v1/fapi/getStopProfit
```

参数:

| 参数 | 值 |
| --- | --- |
| openId | 0 |
| orderId | 54635502191944903 |
| instrument | BTC |

加密连接方法:

```
signParam = timestamp + 'GET' + endpoint名称 + get请求参数
```

示例:

```
1701944491793GET/v1/fapi/getStopProfit?orderId=54635502191944903&instrument=BTC&openId=0
```

加密:

使用"secret_key"作为HMAC SHA256的密钥。将"signParam"作为操作数应用后，获取输出结果，然后进行base64编码。

注意: timestamp值应与header中的相同。"GET"必须大写。

#### POST请求示例

```
POST /v1/fapi/open
```

参数:

| 参数 | 值 |
| --- | --- |
| direction | long |
| positionModel | 0 |
| positionType | execute |
| instrument | ADA |
| leverage | 50 |
| quantityUnit | 1 |
| quantity | 1 |
| contractType | 1 |

加密连接方法:

```
signParam = timestamp + 'POST' + endpoint名称 + Post body参数
```

示例:

```
1701945494169POST/v1/fapi/open{"leverage":"50","quantity":"1","positionType":"execute","contractType":"1","instrument":"ADA","quantityUnit":"1","positionModel":"0","direction":"long"}
```

加密:

使用"secret_key"作为HMAC SHA256的密钥。将"signParam"作为操作数应用后，获取输出结果，然后进行base64编码。

注意: timestamp值应与header中的相同。"POST"必须大写。

## USDT保证金合约API

### 查询未完成订单

查询未完成订单

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/open
```

```
curl "https://api.coinw.com/v1/perpum/orders/open?positionType=moveStopProfitLoss&instrument=BTC"
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| positionType | string | true | null | plan: 限价, execute: 市价, planTrigger: 条件单, moveStopProfitLoss: 追踪止损 |
| page | int | false | 1 | 当前页 |
| pageSize | int | false | 50 | 当前页数据数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | string | 仓位ID |
| userId | Long | 用户ID |
| baseSize | BigDecimal | 描述 |
| createdDate | timestamp | 创建时间 |
| currentPiece | BigDecimal | 当前合约数量 |
| direction | string | long: 开多, short: 开空 |
| frozenFee | BigDecimal | 下单冻结手续费 |
| indexPrice | BigDecimal | 指数触发价格 |
| instrument | string | 交易对 |
| leverage | BigDecimal | 仓位杠杆 |
| liquidateBy | string | 开仓/平仓 |
| margin | BigDecimal | 仓位使用保证金 |
| orderPrice | BigDecimal | 订单价格 |
| orderStatus | string | unFinish: 未成交, part: 部分成交, Finish: 全部成交, Cancel: 已取消 |
| originalType | string | 原始订单类型 |
| posType | string | 仓位类型: plan/planTrigger/execute |
| positionMargin | BigDecimal | 仓位保证金 |
| positionModel | int | 仓位模式: 0-逐仓, 1-全仓 |
| quantity | string | 持有合约或金额 |
| quantityUnit | BigDecimal | 金额单位: 0-USDT, 1-合约, 2-币 |
| status | string | 状态: 开仓/平仓 |
| takerFee | BigDecimal | 吃单手续费率 |
| totalPiece | BigDecimal | 总合约数 |
| updatedDate | string | 最后更新 |

#### 响应示例:

```json
{
  "code": 0,
  "data": {
    "rows": [
      {
        "baseSize": 1,
        "createdDate": 1698211897000,
        "currentPiece": 1000,
        "direction": "short",
        "frozenFee": 44.407308,
        "id": 43308284486163264,
        "indexPrice": 33998.37,
        "instrument": "BTC",
        "leverage": 20,
        "liquidateBy": "manual",
        "makerFee": 0.0004,
        "margin": 1850.3045,
        "orderPrice": 37006.09,
        "orderStatus": "unFinish",
        "originalType": "plan",
        "posType": "plan",
        "positionMargin": 1850.3045,
        "positionModel": 1,
        "processStatus": 0,
        "quantity": 1000,
        "quantityUnit": 1,
        "source": "web",
        "status": "open",
        "takerFee": 0.0006,
        "totalPiece": 1000,
        "updatedDate": 1698211897000,
        "userId": 600003366
      }
    ],
    "total": 0
  },
  "msg": ""
}
```

### 查询待处理订单数量

查询待处理订单数量

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/openQuantity
```

```
curl "https://api.coinw.com/v1/perpum/orders/openQuantity"
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| data | Integer | 待处理订单 |

#### 响应示例:

```json
{
  "code": 0,
  "data": 0,
  "msg": ""
}
```

### 查询个人交易历史

查询个人交易历史

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/trades
```

```
curl "https://api.coinw.com/v1/perpum/orders/trades?instrument=BTC"
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| page | int | false | 1 | 当前页 |
| pageSize | int | false | 50 | 当前页数据数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| closedPiece | integer | 平仓数量 |
| createdDate | long | 交易时间戳 |
| dealPrice | BigDecimal | 成交价格 |
| direction | string | long: 开多, short: 开空 |
| id | long | 交易ID |

### 查询产品信息

查询产品信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/instruments
```

```
curl "https://api.coinw.com/v1/perpum/instruments?name=BTC"
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| name | string | false | null | 交易对 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| base | string | 交易对 |
| defaultLeverage | Integer | 默认杠杆 |
| defaultStopLossRate | BigDecimal | 止损比例 |
| defaultStopProfitRate | BigDecimal | 止盈比例 |
| indexId | Integer | 指数ID/标的资产指数 |
| leverage | String | 支持的杠杆倍数，例如：50x, 100x, 150x |
| makerFee | BigDecimal | 挂单手续费 |
| maxLeverage | Integer | 最大杠杆 |
| minLeverage | Integer | 最小杠杆 |
| maxPosition | BigDecimal | 仓位限制 |
| minSize | BigDecimal | 最小数量 |
| name | String | 交易对 |

### 查看永续合约当前资金费率

查看永续合约当前资金费率

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/fundingRate
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| fundingRate | BigDecimal | 当前资金费率 |
| nextFundingRate | BigDecimal | 预测下一期资金费率 |
| nextSettleTime | long | 下一期结算时间 |

### 查看系统时间

查看系统时间

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/time
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| time | long | 系统时间戳 |

### 查看衍生品仓位档位

查看衍生品仓位档位

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/ladderConfig
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| ladderList | array | 档位列表 |
| - ladderValue | BigDecimal | 档位值 |
| - marginRate | BigDecimal | 保证金率 |
| - maintenanceMarginRate | BigDecimal | 维持保证金率 |

### 张币转换

张币转换

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/pieceConvert
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| quantity | BigDecimal | true | null | 数量 |
| quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| piece | BigDecimal | 张数 |
| coin | BigDecimal | 币数量 |
| usdt | BigDecimal | USDT数量 |

### 查看持仓信息

查看持仓信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | false | null | 方向：long-多，short-空 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | string | 持仓ID |
| userId | long | 用户ID |
| instrument | string | 交易对 |
| direction | string | 方向：long-多，short-空 |
| leverage | BigDecimal | 杠杆倍数 |
| margin | BigDecimal | 保证金 |
| openPrice | BigDecimal | 开仓均价 |
| quantity | BigDecimal | 持仓数量 |
| liquidationPrice | BigDecimal | 强平价格 |
| unrealizedProfit | BigDecimal | 未实现盈亏 |
| positionModel | int | 仓位模式：0-逐仓，1-全仓 |

### 查询全部持仓

查询全部持仓

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions/all
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| positions | array | 持仓列表 |
| - id | string | 持仓ID |
| - userId | long | 用户ID |
| - instrument | string | 交易对 |
| - direction | string | 方向：long-多，short-空 |
| - leverage | BigDecimal | 杠杆倍数 |
| - margin | BigDecimal | 保证金 |
| - openPrice | BigDecimal | 开仓均价 |
| - quantity | BigDecimal | 持仓数量 |
| - liquidationPrice | BigDecimal | 强平价格 |
| - unrealizedProfit | BigDecimal | 未实现盈亏 |
| - positionModel | int | 仓位模式：0-逐仓，1-全仓 |

### 查看历史持仓信息

查看历史持仓信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions/history
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | false | null | 交易对 |
| page | int | false | 1 | 当前页 |
| pageSize | int | false | 50 | 每页数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| rows | array | 历史持仓列表 |
| - id | string | 持仓ID |
| - userId | long | 用户ID |
| - instrument | string | 交易对 |
| - direction | string | 方向：long-多，short-空 |
| - leverage | BigDecimal | 杠杆倍数 |
| - margin | BigDecimal | 保证金 |
| - openPrice | BigDecimal | 开仓均价 |
| - closePrice | BigDecimal | 平仓均价 |
| - quantity | BigDecimal | 持仓数量 |
| - profit | BigDecimal | 盈亏 |
| - positionModel | int | 仓位模式：0-逐仓，1-全仓 |
| - createdDate | long | 创建时间 |
| - closedDate | long | 平仓时间 |
| total | int | 总记录数 |

### 设置持仓模式

设置持仓模式

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/positions/changePositionType
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| positionType | int | true | null | 持仓模式：0-逐仓，1-全仓 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 查看仓位模式

查看仓位模式

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions/getPositionType
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| positionType | int | 持仓模式：0-逐仓，1-全仓 |

### 查看最大可买卖/开仓数量

查看最大可买卖/开仓数量

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/maxSize
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | true | null | 方向：long-多，short-空 |
| leverage | BigDecimal | true | null | 杠杆倍数 |
| positionModel | int | true | null | 持仓模式：0-逐仓，1-全仓 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| maxSize | BigDecimal | 最大可开仓数量 |

### 查看最大可用数量

查看最大可用数量

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/maxAvailSize
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | true | null | 方向：long-多，short-空 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| maxAvailSize | BigDecimal | 最大可用数量 |

### 查看账户最大可转余额

查看账户最大可转余额

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/account/transferAvailable
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| availableBalance | BigDecimal | 可用余额 |

### 调整保证金

调整保证金

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/positions/changeMargin
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | true | null | 方向：long-多，short-空 |
| amount | BigDecimal | true | null | 调整金额 |
| type | int | true | null | 类型：1-增加，2-减少 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 查看杠杆倍数

查看杠杆倍数

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions/getLeverage
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | true | null | 方向：long-多，short-空 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| leverage | BigDecimal | 杠杆倍数 |

### 当前账户的手续费率

当前账户的手续费率

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/account/userLevelFee
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| makerFee | BigDecimal | 挂单手续费率 |
| takerFee | BigDecimal | 吃单手续费率 |

### 下单

下单

#### 请求限制

10 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/open
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | true | null | 方向：long-多，short-空 |
| positionType | string | true | null | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| positionModel | int | true | null | 持仓模式：0-逐仓，1-全仓 |
| leverage | BigDecimal | true | null | 杠杆倍数 |
| quantity | BigDecimal | true | null | 数量 |
| quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |
| orderPrice | BigDecimal | false | null | 订单价格（限价单必填） |
| triggerPrice | BigDecimal | false | null | 触发价格（条件单必填） |
| triggerType | int | false | null | 触发类型：0-最新价，1-指数价，2-标记价 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| orderId | string | 订单ID |

### 批量下单

批量下单

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/batchOpen
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| orders | array | true | null | 订单列表 |
| - instrument | string | true | null | 交易对 |
| - direction | string | true | null | 方向：long-多，short-空 |
| - positionType | string | true | null | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| - positionModel | int | true | null | 持仓模式：0-逐仓，1-全仓 |
| - leverage | BigDecimal | true | null | 杠杆倍数 |
| - quantity | BigDecimal | true | null | 数量 |
| - quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |
| - orderPrice | BigDecimal | false | null | 订单价格（限价单必填） |
| - triggerPrice | BigDecimal | false | null | 触发价格（条件单必填） |
| - triggerType | int | false | null | 触发类型：0-最新价，1-指数价，2-标记价 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| orderIds | array | 订单ID列表 |

### 批量平仓

批量平仓

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/batchClose
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| positions | array | true | null | 持仓列表 |
| - openId | string | true | null | 持仓ID |
| - quantity | BigDecimal | true | null | 平仓数量 |
| - quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |
| - positionType | string | true | null | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| - orderPrice | BigDecimal | false | null | 订单价格（限价单必填） |
| - triggerPrice | BigDecimal | false | null | 触发价格（条件单必填） |
| - triggerType | int | false | null | 触发类型：0-最新价，1-指数价，2-标记价 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| orderIds | array | 订单ID列表 |

### 撤单

撤单

#### 请求限制

10 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/cancel
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| orderId | string | true | null | 订单ID |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 批量撤单

批量撤单

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/batchCancel
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| orderIds | array | true | null | 订单ID列表 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 修改订单

修改订单

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/edit
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| orderId | string | true | null | 订单ID |
| orderPrice | BigDecimal | false | null | 新订单价格 |
| triggerPrice | BigDecimal | false | null | 新触发价格 |
| quantity | BigDecimal | false | null | 新数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 平仓

平仓

#### 请求限制

10 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/close
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |
| quantity | BigDecimal | true | null | 平仓数量 |
| quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |
| positionType | string | true | null | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| orderPrice | BigDecimal | false | null | 订单价格（限价单必填） |
| triggerPrice | BigDecimal | false | null | 触发价格（条件单必填） |
| triggerType | int | false | null | 触发类型：0-最新价，1-指数价，2-标记价 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| orderId | string | 订单ID |

### 市价仓位全平

市价仓位全平

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/closeAll
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | true | null | 交易对 |
| direction | string | false | null | 方向：long-多，short-空（不传则全平） |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 一键反向

一键反向

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/orders/closeAndOpenReverse
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |
| leverage | BigDecimal | true | null | 反向开仓杠杆倍数 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 获取订单信息

获取订单信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/detail
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| orderId | string | true | null | 订单ID |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | string | 订单ID |
| userId | long | 用户ID |
| instrument | string | 交易对 |
| direction | string | 方向：long-多，short-空 |
| posType | string | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| orderPrice | BigDecimal | 订单价格 |
| quantity | BigDecimal | 数量 |
| status | string | 状态：open-开仓，close-平仓 |
| orderStatus | string | 订单状态：unFinish-未成交，part-部分成交，Finish-全部成交，Cancel-已取消 |
| createdDate | long | 创建时间 |
| updatedDate | long | 更新时间 |

### 查看历史订单记录

查看历史订单记录（近七天）

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/history
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | false | null | 交易对 |
| status | string | false | null | 状态：open-开仓，close-平仓 |
| orderStatus | string | false | null | 订单状态：unFinish-未成交，part-部分成交，Finish-全部成交，Cancel-已取消 |
| page | int | false | 1 | 当前页 |
| pageSize | int | false | 50 | 每页数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| rows | array | 订单列表 |
| - id | string | 订单ID |
| - userId | long | 用户ID |
| - instrument | string | 交易对 |
| - direction | string | 方向：long-多，short-空 |
| - posType | string | 订单类型：plan-限价，execute-市价，planTrigger-条件单 |
| - orderPrice | BigDecimal | 订单价格 |
| - quantity | BigDecimal | 数量 |
| - status | string | 状态：open-开仓，close-平仓 |
| - orderStatus | string | 订单状态：unFinish-未成交，part-部分成交，Finish-全部成交，Cancel-已取消 |
| - createdDate | long | 创建时间 |
| - updatedDate | long | 更新时间 |
| total | int | 总记录数 |

### 查看成交明细

查看成交明细（近三天）

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/orders/fills
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| instrument | string | false | null | 交易对 |
| page | int | false | 1 | 当前页 |
| pageSize | int | false | 50 | 每页数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| rows | array | 成交列表 |
| - id | string | 成交ID |
| - orderId | string | 订单ID |
| - instrument | string | 交易对 |
| - direction | string | 方向：long-多，short-空 |
| - price | BigDecimal | 成交价格 |
| - quantity | BigDecimal | 成交数量 |
| - fee | BigDecimal | 手续费 |
| - createdDate | long | 成交时间 |
| total | int | 总记录数 |

### 查看仓位保证金率

查看仓位保证金率

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/positions/marginRate
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| marginRate | BigDecimal | 保证金率 |
| maintenanceMarginRate | BigDecimal | 维持保证金率 |

### 查看止盈止损信息

查看止盈止损信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/stopProfitLoss
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| stopProfit | BigDecimal | 止盈价格 |
| stopLoss | BigDecimal | 止损价格 |

### 设置止盈止损

设置止盈止损

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/stopProfitLoss
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |
| stopProfit | BigDecimal | false | null | 止盈价格 |
| stopLoss | BigDecimal | false | null | 止损价格 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 添加分批止盈止损

添加分批止盈止损

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/batchTPSL/add
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |
| tpslList | array | true | null | 止盈止损列表 |
| - price | BigDecimal | true | null | 价格 |
| - quantity | BigDecimal | true | null | 数量 |
| - quantityUnit | int | true | null | 单位：0-USDT，1-张数，2-币 |
| - type | int | true | null | 类型：1-止盈，2-止损 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 修改分批止盈止损

修改分批止盈止损

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/batchTPSL/update
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| id | string | true | null | 止盈止损ID |
| price | BigDecimal | false | null | 新价格 |
| quantity | BigDecimal | false | null | 新数量 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 查看移动止盈止损信息

查看移动止盈止损信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/moveTPSL
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | string | 移动止盈止损ID |
| openId | string | 持仓ID |
| callbackRate | BigDecimal | 回调率 |
| triggerPrice | BigDecimal | 激活价格 |
| quantity | BigDecimal | 数量 |
| quantityUnit | int | 单位：0-USDT，1-张数，2-币 |

### 设置移动止盈止损

设置移动止盈止损

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/moveTPSL
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| openId | string | true | null | 持仓ID |
| callbackRate | BigDecimal | true | null | 回调率 |
| triggerPrice | BigDecimal | false | null | 激活价格 |
| quantity | BigDecimal | true | null | 数量 |
| quantityUnit | int | false | null | 单位：0-USDT，1-张数，2-币 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| success | boolean | 是否成功 |

### 查看合约万能金信息

查看合约万能金信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/account/almightyGoldInfo
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| startTime | Long | false | null | 有效期起始时间 |
| endTime | Long | false | null | 有效期截止时间 |
| type | Integer | false | 1,2 | 0:待生效 1: 未使用 2:已使用 3:已失效 4发放失败 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| id | Long | 万能金id |
| assetsOut | Integer | 转出资产是否失效 1：是 0：否 |
| agRecordId | Integer | 发放记录id |
| kyc | Integer | 是否要求高级kyc使用 1：是 0:否 |
| currentAmount | BigDecimal | 剩余金额 |
| totalAmount | BigDecimal | 万能金总金额 |
| type | Integer | 0:待生效 1: 未使用 2:已使用 3:已失效 4发放失败 |
| startTime | Date | 有效期起始时间 |
| endTime | Date | 有效期截止时间 |
| remark | String | 备注 |
| createdDate | Date | 创建时间 |
| updateDate | Date | 更新时间 |
| userId | Long | 用户id |

#### 响应示例:

```json
{
  "code": 0,
  "data": [
    {
      "agRecordId": 69,
      "assetsOut": 0,
      "createdDate": 1698650673000,
      "currentAmount": 1,
      "endTime": 1698909873000,
      "id": 70,
      "kyc": 0,
      "name": "万能金",
      "processStatus": 0,
      "startTime": 1698650673000,
      "totalAmount": 1,
      "type": 1,
      "updateDate": 1698650673000,
      "remark": "备注",
      "userId": 600003366
    }
  ],
  "msg": ""
}
```

### 设置合约万能金状态

设置合约万能金状态

#### 请求限制

5 requests/s

#### HTTP请求

```
POST /v1/perpum/account/almightyGoldInfo
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
| --- | --- | --- | --- | --- |
| status | string | true | null | 状态 1：开启 0：关闭 |

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| code | int | 状态码 |
| msg | string | 消息 |

#### 响应示例:

```json
{
  "code": 0,
  "msg": ""
}
```

### 获取用户资产信息

获取用户资产信息

#### 请求限制

10 requests/s

#### HTTP请求

```
GET /v1/perpum/account/getUserAssets
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| availableMargin | BigDecimal | 可用保证金余额（含万能金） |
| userId | Long | 用户id |
| almightyGold | BigDecimal | 可用万能金余额 |
| availableUsdt | BigDecimal | 可用USDT余额 |
| alMargin | BigDecimal | 持仓资产 |
| alFreeze | BigDecimal | 冻结资产 |
| time | Long | 时间戳 |

#### 响应示例:

```json
{
  "code": 0,
  "data": [{
    "availableMargin": 996660.6064387699998485,
    "userId": 600001274,
    "almightyGold": 0,
    "availableUsdt": 996660.6064387699998485,
    "alMargin": 10000,
    "alFreeze": 10000,
    "time": 1705785391000
  }],
  "msg": ""
}
```

### 查看所有币对行情信息

查看所有币对行情信息

#### 请求限制

5 requests/s

#### HTTP请求

```
GET /v1/perpumPublic/tickers
```

#### 参数

无参数

#### 响应

| 参数 | 类型 | 描述 |
| --- | --- | --- |
| contract_id | Integer | 合约id |
| name | string | 合约名称 |
| base_coin | string | 合约币 |
| quote_coin | string | USDT |
| price_coin | string | 合约币 |
| max_leverage | int | 最大杠杆 |
| contract_size | BigDecimal | 面值(一手最小值) |
| last_price | BigDecimal | 最新价 |
| high | BigDecimal | 最高价 |
| low | BigDecimal | 最低价 |
| rise_fall_rate | BigDecimal | 涨跌幅 |
| total_volume | BigDecimal | 成交量 |
| fair_price | BigDecimal | 标记价格 |
| funding_rate | BigDecimal | 资金费率 |
| next_funding_rate | BigDecimal | 预测下一期资金费率 |
| next_funding_time | long | 下一期结算时间 |

## WebSocket API

### K线

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | subscribe | 订阅 |
| args | spot/candle-${granularity}:${symbol} | ${granularity}为粒度[1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 1w,1M],${symbol}为所需订阅的币种，例如,LTC-USDT |

#### 返回字段

| 参数名称 | 数据类型 | 描述 |
| --- | --- | --- |
| channel | string | 订阅的通道 |
| subject | string | 所属科目 |
| data数组 | | |
| 0 | string | 时间(毫秒数) |
| 1 | bigdecimal | 开盘价 |
| 2 | bigdecimal | 收盘价 |
| 3 | bigdecimal | 最高 |
| 4 | bigdecimal | 最低 |
| 5 | bigdecimal | 成交量 |
| 6 | bigdecimal | 成交额 |

#### 响应示例:

```json
{
  "channel": "spot/candle-15m:BTC-USDT",
  "subject": "spot/candle-15m",
  "data":"[\"1681875900000\",\"30214.56\",\"30182.48\",\"30214.56\",\"30182.48\",\"12.9646\",\"391493.29663\"]"
}
```

### 订单薄

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | subscribe | 订阅 |
| args | spot/level2:${symbol} | {symbol}为所需订阅的币种，例如,LTC-USDT |

#### 返回字段

| 参数名称 | 数据类型 | 描述 |
| --- | --- | --- |
| channel | string | 订阅的通道 |
| subject | string | 所属科目 |
| data | | |
| startSeq | string | 开始序号 |
| endSeq | string | 结束序号 |
| 卖方二维数组 | | |
| 0 | bigdecimal | 单价 |
| 1 | bigdecimal | 数量 |
| 2 | string | 序号 |
| 买方二维数组 | | |
| 0 | bigdecimal | 单价 |
| 1 | bigdecimal | 数量 |
| 2 | string | 序号 |

#### 响应示例:

```json
{
  "channel":"spot/level2:BTC-USDT",
  "subject":"spot/level2",
  "data":"{\"startSeq\":2130205870,\"endSeq\":2130205870,\"asks\":[[\"30344.39\",\"0.0701\",\"2130205870\"]],\"bids\":[]}"
}
```

### 成交历史

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | subscribe | 订阅 |
| args | spot/match:${symbol} | {symbol}为所需订阅的币种，例如,LTC-USDT |

#### 返回字段

| 参数名称 | 数据类型 | 描述 |
| --- | --- | --- |
| channel | string | 订阅的通道 |
| subject | string | 所属科目 |
| data | | |
| price | bigdecimal | 单价 |
| side | string | 方向(BUY,买,SELL,卖) |
| size | string | 数量 |
| symbol | string | 币对 |
| time | string | 时间(毫秒数) |

#### 响应示例:

```json
{
  "channel":"spot/match:BTC-USDT",
  "subject":"spot/match",
  "data":"[{\"price\":\"30077.88\",\"seq\":\"79895588\",\"side\":\"BUY\",\"size\":\"1.2488\",\"symbol\":\"78\",\"time\":\"1681891021015\"}]"
}
```

### 资产及订单

#### 接入url

wss://ws.futurescw.com

#### 心跳信息

心跳信息请求示例如下:
客户端发送 {"event":"ping"}  服务端响应  {"event":"pong"}
建议定时10秒 ping pong

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | ping | 心跳信息 |

#### 登录

登录请求示例如下:
{"event":"login","params":{"api_key":"xxx","passphrase":"xxx"}}

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | login | 登录 |
| params | | |
| api_key | xxx | apikey |
| passphrase | xxx | passphrase |

### 订阅订单

订阅订单 请求示例如下:
{"event":"sub","params":{"biz":"exchange","type":"order"}}

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | sub | 订阅 |
| params | | |
| biz | exchange | 交易 |
| type | order | 类型 |

#### 返回字段

| 参数名称 | 数据类型 | 描述 |
| --- | --- | --- |
| biz | string | 交易 |
| type | string | 类型 |
| data | | |
| type | string | 类型 |
| time | datetime | 下单时间 |
| product_id | string | 产品id |
| order_id | string | 订单号 |
| client_id | string | 客户端id |
| size | string | 数量 |
| remaining_size | string | 剩余数量 |
| price | string | 订单价格 |
| side | string | 方向-买卖 |
| order_type | string | 订单类型:LIMIT-限价，MARKET-市价 |
| reason | string | 原因 |

#### 响应示例:

```json
{
  "biz": "exchange",
  "data": [{
    "type": "DONE",
    "time": 1697557265740,
    "product_id": "78",
    "order_id": 4616004900217272378,
    "client_id": "",
    "size": "0.001",
    "remaining_size": "0",
    "price": "20000",
    "side": "BUY",
    "order_type": "LIMIT",
    "reason": "FILLED"
  }],
  "type": "order"
}
```

### 订阅资产

订阅资产 请求示例如下:
{"event":"sub","params":{"biz":"exchange","type":"assets"}}

#### 请求参数

| 参数名称 | 值 | 描述 |
| --- | --- | --- |
| event | sub | 订阅 |
| params | | |
| biz | exchange | 交易 |
| type | assets | 类型 |

#### 返回字段

| 参数名称 | 数据类型 | 描述 |
| --- | --- | --- |
| biz | string | 交易 |
| type | string | 类型 |
| data | | |
| currency | string | 币种 |
| available | string | 可用 |
| hold | string | 冻结 |

#### 响应示例:

```json
{
  "biz": "exchange",
  "data": [{
    "currency": "USDT",
    "available": "9999.9",
    "hold": "0.1"
  }],
  "type": "assets"
}
```
