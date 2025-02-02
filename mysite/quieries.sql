SELECT "shopapp_product"."id",
       "shopapp_product"."name",
       "shopapp_product"."description",
       "shopapp_product"."price",
       "shopapp_product"."discount",
       "shopapp_product"."created_at",
       "shopapp_product"."archived",
       "shopapp_product"."created_by_i
d",
       "shopapp_product"."preview"
FROM "shopapp_product"
WHERE NOT "shopapp_product"."archived"
ORDER BY "shopapp_product"."name" ASC;
args
=(); alias
=default
