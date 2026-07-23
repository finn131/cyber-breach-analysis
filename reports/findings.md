
# Findings

## Key Insights

- The dataset contains **777** breach records and **777** unique services.
- There are **720** unique domains, with **38** rows missing a domain value.
- **737** records are verified, while **40** are unverified.
- The dataset contains **61** sensitive entries, **16** spam-list entries, **5** malware-related entries, and **6** subscription-free entries.
- The cumulative `PwnCount` across the dataset is **13,517,282,665** impacted accounts.
- The largest breach in the file is **772,904,991** impacted accounts.
- Breach activity peaks in **2016**, which contains **101** records.

## Important Statistics

- Most common data class: **email addresses** (771 occurrences)
- Most repeated domain: **ogusers.com** (4 occurrences)
- Naming pattern highlights: **45** services contain digits, **123** names are five characters or fewer, and **464** titles match their service names.

## Interesting Findings

- Every `Name` value is unique, so service-name frequency is not concentrated in repeated services.
- Repeated domains are a stronger indicator of overlap than service names in this dataset.
- The largest breach entries are dominated by credential-focused incidents rather than low-impact records.

## Recommendations

- Prioritize repeated domains and high-`PwnCount` incidents when reviewing exposure risk.
- Group future analysis by data class, because service names are mostly one-off labels.
- Add an automated refresh flow so updated breach files can be cleaned and re-plotted quickly.
