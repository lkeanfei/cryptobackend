CREATE OR REPLACE VIEW cryptoanalysis.TechnicalsAvailableMarkets
AS
SELECT DISTINCT(`exchange`) from cryptoanalysis.technicals

CREATE OR REPLACE VIEW cryptoanalysis.TechnicalsAvailableCoinPairs
AS
SELECT DISTINCT(`coinpair`) from cryptoanalysis.technicals order by coinpair

python manage.py inspectdb  > 2May2019.model.py

