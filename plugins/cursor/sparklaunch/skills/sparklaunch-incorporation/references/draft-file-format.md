# Incorporation Draft File Format

Use this reference to help a user prepare the complete non-address portion of an incorporation draft. Never ask the user to paste the completed file or any physical address into chat.

## Safe preparation

1. Start from `synthetic-single-founder-draft.json` in this directory.
2. For a real case, have the user copy the file to their own device and replace the synthetic ordinary company data.
3. Keep every declared field; the draft is a complete replacement, not a partial patch. Remove `participants` only when there are no non-founder participants.
4. Use JSON numbers for equity, share, and par-value fields; do not quote them and do not use booleans as numbers.
5. Keep `entity_type` as `delaware_c_corporation` and `jurisdiction` as `DE`.
6. Use one stable UUID `participant_key` per person. Reuse those keys in governance assignments and founder share allocations.
7. Non-founder participant roles may only be `incorporator`, `director`, `officer`, `signer`, or `responsible_party`.
8. Do not include `address`, `addresses`, `business_address`, `mailing_address`, street, city, region/state, postal/ZIP, or country-location fields. SparkLaunch rejects a structured draft or draft file containing them. Each participant enters their own address in the authenticated SparkLaunch Action Center, and the filing signer completes the protected company address task there.
9. Do not include SSN/TIN values, identity documents, biometrics, payment credentials, signatures, private attestations, provider URLs/tokens, invitation tokens, or checkpoint locators.
10. Keep the completed object no larger than 256KB when serialized as UTF-8 JSON. Pass exactly one input: the object as `draft`, or a host-supported JSON file reference as `draft_file`. Never send both.

The controlled reviewer fixture may use `synthetic-single-founder-draft.json` unchanged. It contains synthetic `example.com` data and must never be represented as a real filing instruction or production filing record.
