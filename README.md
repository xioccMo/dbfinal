# gtmdDatabase

##### 第四次更新
更新时间：2019年12月17日 22:55:54  
测试已完成情况：
- [x] test_add_book.py	 
- [x] test_add_funds.py
- [x] test_add_stock_level.py
- [x] test_create_store.py	
- [x] test_login.py	
- [x] test_new_order.py	
- [x] test_password.py	
- [x] test_payment.py	
- [x] test_register.py  

添加的功能有：  
- [x] 收货
- [x] 发货
- [x] 取消订单
- [x] 根据id查询订单
- [x] 分别按进行中和已结束的分类，按时间顺序查询所有订单
- [x] 逾期自动取消订单
- [ ] 评论功能
##### 第三次更新
更新时间：2019年12月17日 22:55:54 

##### 第二次更新
更新时间：2019年12月17日 05:54:48  

##### 第一次更新
更新时间：2019年12月16日 13:51:55  

### 总体情况：
#### 功能
实现一个提供网上购书功能的网站后端。<br>
网站支持书商在上面开商店，购买者可能通过网站购买。<br>
卖家和买家都可以注册自己的账号。<br>
一个卖家可以开一个或多个网上商店，
买家可以为自已的账户充值，在任意商店购买图书。<br>
支持下单->付款->发货->收货，流程。<br>

#### 项目目录结构
```
│  gtmddatabase.sql
│  Pipfile
│  Pipfile.lock
│  README.md
│  readmeXm.md
│  readori.md
│  requirements.txt
├─fe
│  │  conf.py
│  │  conftest.py
│  │  __init__.py
│  │
│  ├─access   功能实现
│  │  │  auth.py
│  │  │  book.py
│  │  │  buyer.py
│  │  │  new_buyer.py
│  │  │  new_function.py
│  │  │  new_seller.py
│  │  │  seller.py
│  │  │  __init__.py
│  │
│  ├─bench   添加性能测试
│  │  │  bench.md
│  │  │  run.py
│  │  │  session.py
│  │  │  workload.py
│  │  │  __init__.py
│  │
│  ├─data   数据库
│  │      book.db
│  │      scraper.log
│  │      scraper.py
│  │
│  ├─test  添加测试功能
│  │  │  gen_book_data.py
│  │  │  test.md
│  │  │  test_add_book.py
│  │  │  test_add_funds.py
│  │  │  test_add_stock_level.py
│  │  │  test_auto_cancel.py
│  │  │  test_bench.py
│  │  │  test_cancel_order.py
│  │  │  test_change_received.py
│  │  │  test_change_unreceived.py
│  │  │  test_create_store.py
│  │  │  test_login.py  
│  │  │  test_new_order.py
│  │  │  test_password.py
│  │  │  test_payment.py
│  │  │  test_register.py
│  │  │  test_track_order.py
│  │  │  test_track_order_by_order_id.py
│  │  │  __init__.py
│
└─gtmd
    │  app.py
    │  config.py
    │  db.py
    │  monitor.py
    │  tokenMethods.py
    │  __init__.py
    │
    ├─blueprints
    │  │  auth.py
    │  │  buyer.py
    │  │  seller.py
    │  │  shutdown.py
    │  │  __init__.py
    │  
    │
    ├─models
    │  │  Book.py
    │  │  Order.py
    │  │  Orderdetail.py
    │  │  PendingOrder.py
    │  │  Store.py
    │  │  User.py
    │  │  __init__.py
 ```   
 
 
#### 文件逻辑
blueprints ： 类的功能实现
models ： 类的说明


#### 对应接口功能
1.实现对应接口的功能，见doc下面的.md文件描述 （60%分数）<br>  

其中包括：

1)用户权限接口，如注册、登录、登出、注销<br>    auth.py

2)买家用户接口，如充值、下单、付款<br>   buyer.py

3)卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存<br>   seller.py

通过对应的功能测试，所有test case都pass <br>
测试下单及付款两个接口的性能（最好分离负载生成和后端），测出支持的每分钟交易数，延迟等 <br>

2.为项目添加其它功能 ：（40%分数）<br>

1)实现后续的流程 <br>
发货 -> 收货

2)搜索图书 <br>   
用户可以通过关键字搜索，参数化的搜索方式；
如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
如果显示结果较大，需要分页
(使用全文索引优化查找)
待实现

3)订单状态，订单查询和取消定单<br>
用户可以查自已的历史订单，用户也可以取消订单。<br>
取消定单（可选项，加分 +5~10），买家主动地取消定单，如果买家下单经过一段时间超时后，如果买家未付款，定单也会自动取消。 <br>

#### 版本控制，测试驱动开发
软件开发的基础流程  面向对象程序设计、测试驱动开发、版本控制、调试、设计模式

测试驱动开发，英文全称Test-Driven Development，简称TDD，是一种不同于传统软件开发流程的新型的开发方法。它要求在编写某个功能的代码之前
先编写测试代码，然后只编写使测试通过的功能代码，通过测试来推动整个开发的进行。这有助于编写简洁可用和高质量的代码，并加速开发过程。

软件系统的版本号由3部分构成，即主版本号+次版本号+修改号。主版本号1位，只有当系统在结构和功能上有重大突破改进后才发生变化；
次版本号有2位；修改号8位，采用提交时的日期，当系统进行任何修改后，包括数据库结构发生变化，修改号都要随之改变。例如：Ver3.31.19990317 


#### 通过测试并计算代码覆盖率

#### 基于Lucene的图书全文搜索引擎
用户可以通过关键字搜索，参数化的搜索方式；
如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
如果显示结果较大，需要分页
(使用全文索引优化查找)
待实现
