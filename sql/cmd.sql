insert into jall
SELECT price.S_INFO_WINDCODE, price.TRADE_DT, price.S_DQ_PCTCHANGE, price.S_DQ_VOLUME, price.S_DQ_AMOUNT, price.S_DQ_ADJPRECLOSE, price.S_DQ_ADJOPEN, price.S_DQ_ADJHIGH, price.S_DQ_ADJLOW, price.S_DQ_ADJCLOSE, big.S_DQ_FREETURNOVER, big.S_PQ_ADJHIGH_52W, big.S_PQ_ADJLOW_52W, big.FREE_SHARES_TODAY
FROM price
INNER JOIN big
ON (price.S_INFO_WINDCODE=big.S_INFO_WINDCODE AND price.TRADE_DT=big.TRADE_DT);


-- select count(*) from big where trade_dt >= "20160000";
-- select count(*) from price where trade_dt >= "20160000";

-- select count(*) from big where (trade_dt >= "20150000" and trade_dt < "20160000");
-- select count(*) from price where (trade_dt >= "20150000" and trade_dt < "20160000");

-- create index price_index on price(S_INFO_WINDCODE, TRADE_DT);
-- create index big_index on big(S_INFO_WINDCODE, TRADE_DT);

-- mysql -B -uroot st -e "SELECT * FROM jall where (dt >='20150000' and dt < '20160000');"  | sed "s/'/\'/;s/\t/,/g;s/\n//g" > 2015.cc