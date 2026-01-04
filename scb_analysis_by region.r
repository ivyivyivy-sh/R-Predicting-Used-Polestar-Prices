library(pxweb)
library(dplyr)  # For data manipulation

# Define the URL
scb_url <- "https://api.scb.se/OV0104/v1/doris/en/ssd/START/TK/TK1001/TK1001A/PersBilarDrivMedel"

# Function to get top 20 cities for a given year
get_top20_for_year <- function(year) {
  # Determine months: for 2025, up to M11; for others, M01 to M12
  if (year == 2025) {
    months <- sprintf("%sM%02d", year, 1:11)
  } else {
    months <- sprintf("%sM%02d", year, 1:12)
  }
  
  # Query for all regions, Electricity, for the year's months
  scb_query <- list(
    "Region" = "*",  # All municipalities
    "Drivmedel" = "120",  # Electricity
    "Tid" = months
  )
  
  # Fetch data
  scb_data <- pxweb_get(url = scb_url, query = scb_query)
  
  # Convert to data frame
  df <- as.data.frame(scb_data, column.name.type = "text", variable.value.type = "text")
  
  # Identify the value column (last column)
  value_col <- colnames(df)[ncol(df)]
  
  # Ensure value column is numeric
  df[[value_col]] <- as.numeric(df[[value_col]])
  
  # Group by region, sum the values for the year
  df_aggregated <- df %>%
    group_by(region) %>%
    summarise(total_electric_cars = sum(.data[[value_col]], na.rm = TRUE)) %>%
    arrange(desc(total_electric_cars)) %>%
    head(20)
  
  # Add year column
  df_aggregated$year <- year
  
  return(df_aggregated)
}

# Get top 20 for each year
years <- 2021:2025
top20_list <- lapply(years, get_top20_for_year)

# Combine into one data frame
df_all_top20 <- bind_rows(top20_list)

# View the combined data
print(df_all_top20)

# Save to CSV
write.csv(df_all_top20, "top_20_cities_electric_cars_by_year.csv", row.names = FALSE)
print("Top 20 cities by year saved to top_20_cities_electric_cars_by_year.csv")

# Optional: Save separate CSVs for each year
for (year in years) {
  df_year <- df_all_top20 %>% filter(year == !!year)
  write.csv(df_year, paste0("top_20_cities_", year, ".csv"), row.names = FALSE)
  print(paste("Saved top 20 for", year, "to top_20_cities_", year, ".csv"))
}