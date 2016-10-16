-- create table b2015 like big;
-- insert into b2015 select * from big where (trade_dt >= "20150000" and trade_dt < "20160000");

-- create table p2015 like price;
-- insert into p2015 select * from price where (trade_dt >= "20150000" and trade_dt < "20160000");

CREATE TABLE `jall` (
  `code` varchar(40) DEFAULT NULL COMMENT 'Wind代码',
  `dt` varchar(8) DEFAULT NULL COMMENT '交易日期',

  `rate` decimal(20,4) DEFAULT NULL COMMENT '涨跌幅(%)',
  `volumn` decimal(20,4) DEFAULT NULL COMMENT '成交量(手)',
  `amount` decimal(20,4) DEFAULT NULL COMMENT '成交金额(千元)',
  `pe` decimal(20,4) DEFAULT NULL COMMENT '复权昨收盘价(元)',
  `s` decimal(20,4) DEFAULT NULL COMMENT '复权开盘价(元)',
  `high` decimal(20,4) DEFAULT NULL COMMENT '复权最高价(元)',
  `low` decimal(20,4) DEFAULT NULL COMMENT '复权最低价(元)',
  `e` decimal(20,4) DEFAULT NULL COMMENT '复权收盘价(元)',

  `turnover` decimal(20,4) DEFAULT NULL COMMENT '换手率(基准.自由流通股本)',
  `shares` decimal(20,4) DEFAULT NULL COMMENT '当日自由流通股本'
);

insert into jall
SELECT price.S_INFO_WINDCODE, price.TRADE_DT, price.S_DQ_PCTCHANGE, price.S_DQ_VOLUME, price.S_DQ_AMOUNT, price.S_DQ_ADJPRECLOSE, price.S_DQ_ADJOPEN, price.S_DQ_ADJHIGH, price.S_DQ_ADJLOW, price.S_DQ_ADJCLOSE, big.S_DQ_FREETURNOVER, big.FREE_SHARES_TODAY
FROM price
INNER JOIN big
ON (price.S_INFO_WINDCODE=big.S_INFO_WINDCODE AND price.TRADE_DT=big.TRADE_DT);
