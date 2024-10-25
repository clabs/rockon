# Import Pretix vouchers

Vouchers from Pretix CSV export can be imported to the system.

```bash
python ./src/manage.py importvoucher \
    --crew b381314d-470e-41a1-958c-d667bd988c9a \
    --vouchertype "Crew Gast Freitag" \
    --eventday c0b0b4d3-e104-40ff-84db-bbeafb4f0ca0
    ./vouchers.csv
```
