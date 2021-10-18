```json
// http://api.exchangeratesapi.io/v1/timeseries?access_key={{access_key}}&start_date=2021-05-01&end_date=2021-05-25

{
    "error": {
        "code": "function_access_restricted",
        "message": "Access Restricted - Your current Subscription Plan does not support this API Function."
    }
}
```

```json
// http://api.exchangeratesapi.io/v1/2021-10-11?access_key={{access_key}}&base=USD

{
    "error": {
        "code": "base_currency_access_restricted",
        "message": "An unexpected error ocurred. [Technical Support: support@apilayer.com]"
    }
}
```

http://api.exchangeratesapi.io/v1/2021-10-11?access_key={{access_key}}&base=EUR
