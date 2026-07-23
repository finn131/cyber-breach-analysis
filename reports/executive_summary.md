
# Executive Summary

## Project Objective

This project analyzes a cybersecurity breach dataset to understand breach scale, exposed data types, and recurring patterns across services and domains.

## Dataset Overview

- Records: **777**
- Unique services: **777**
- Unique domains: **720**
- Verified records: **737**
- Unverified records: **40**

## Main Findings

- Service names are unique, so the more meaningful repetition appears at the domain level.
- `Email addresses` is the most common data class, followed by `Passwords` and `Usernames`.
- The largest breach in the dataset impacted **772,904,991** accounts.
- Breach activity is heaviest in **2016**.

## Future Improvements

- Add automated validation checks for new raw files.
- Extend the analysis with sector, region, or time-to-disclosure views.
- Build a simple refresh script to regenerate the cleaned data and figures on demand.
