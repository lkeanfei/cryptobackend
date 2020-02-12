CREATE OR REPLACE VIEW cryptoanalysis.TechnicalsAvailableMarkets
AS
SELECT DISTINCT(`exchange`) from cryptoanalysis.technicals

CREATE OR REPLACE VIEW cryptoanalysis.TechnicalsAvailableCoinPairs
AS
SELECT DISTINCT(`coinpair`) from cryptoanalysis.technicals order by coinpair

use cryptoanalysis;
CREATE OR REPLACE VIEW cryptoanalysis.GeckoFundamentalsView
AS
SELECT gf.startTime , gf.coinid , gf.BlockTime, gf.Developer , gf.Community , gf.Liquidity, gf.PublicInterest , gc.description ,gc.small_img_url , gc.thumb_img_url from cryptoanalysis.GeckoFundamentals as gf
INNER Join GeckoCoin as gc on gc.id = gf.coinid


use cryptoanalysis;
CREATE OR REPLACE VIEW cryptoanalysis.HourlyDataTechnicalsView
AS
SELECT hd.startTime, hd.market, hd.coinpair , hd.open, hd.high , hd.low,  hd.close, hd.volume, technicals.pricechangepct , technicals.unusualvolume , technicals.macdindicator from cryptoanalysis.HourlyData as hd
INNER JOIN technicals as technicals on hd.startTime = technicals.startTime and hd.market = technicals.exchange and hd.coinpair = technicals.coinpair

python manage.py inspectdb  > 2May2019.model.py

python manage.py inspectdb HourlyDataCoinpair > HourlyDataCoinpair.model.py