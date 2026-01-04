library(pxweb)

# Define the URL
scb_url <- "https://api.scb.se/OV0104/v1/doris/en/ssd/START/TK/TK1001/TK1001A/PersBilarDrivMedel"

# Create the query list based on the provided JSON
scb_query <- list(
  "Region" = "00",
  "Drivmedel" = "120",  # Updated to match the JSON (previously was "140")
  "Tid" = c(
    paste0(rep(2021:2024, each = 12), "M", sprintf("%02d", 1:12)),
    paste0("2025M", sprintf("%02d", 1:11))  # Up to 2025M11 as in the JSON
  )
)

# Fetch the data (response format defaults to "px" as in the JSON)
scb_data <- pxweb_get(url = scb_url, query = scb_query)

# Convert to a standard R data frame
df_scb <- as.data.frame(scb_data, column.name.type = "text", variable.value.type = "text")

# Next steps: View and save the data
# View the first few rows in the console
print(head(df_scb))

# Save to CSV
write.csv(df_scb, "scb_drivmedel_120_2021_2025.csv", row.names = FALSE)
print("Data saved to scb_drivmedel_120_2021_2025.csv")

