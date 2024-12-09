
CREATE TABLE payments_fact (
    id UInt64,
    school_id UInt64,
    semester_id UInt64,
    currency_code String,
    total_amount Float64,
    status UInt8,
    fee_amount Nullable(Float64),
    claim_amount Nullable(Float64),
    gift_amount Nullable(Float64),
    payment_type_id UInt64,
    user_id UInt64,
    payment_order_id Nullable(UInt64),
    created String
) ENGINE = MergeTree()
ORDER BY (id);

CREATE TABLE user_dim (
    user_id UInt64,
    payment_user_id UInt64,
    payment_email String,
    created String
) ENGINE = MergeTree()
ORDER BY (user_id);

CREATE TABLE time_dim (
    day Date,
    month UInt8,
    year UInt16,
    quarter UInt8,
    created String
) ENGINE = MergeTree()
ORDER BY (year);

CREATE TABLE invoice_dim (
    id UInt64, 
    type String,
    entity_id String,
    amount Float64
) ENGINE = MergeTree()
ORDER BY (id, type);
