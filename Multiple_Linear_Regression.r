# --- 1. Load Libraries & Data ---
library(tidyverse)
library(car) # For VIF (Multicollinearity check)

# Load your latest dataset
df <- read.csv("polestar_blocket_listings_20251231_180428 - Target Data.csv")

# --- 2. Data Cleaning & Preparation ---
# VG Step: Group infrequent locations to avoid "leverage 1" errors and "new levels" errors
top_locations <- df %>%
  count(Plats) %>%
  filter(n >= 10) %>% # Keep cities with 10+ listings
  pull(Plats)

polestar_data <- df %>%
  rename(
    Price = Försäljningspris.SEK.,
    Year = Modellår,
    Model = Modell,
    Location = Plats
  ) %>%
  mutate(
    # Use Mil as requested (Km / 10)
    Mil = Miltal..mil. / 10,
    Model = as.factor(Model),
    # Simplify Location for a more stable model
    Location = factor(ifelse(Location %in% top_locations, as.character(Location), "Other"))
  ) %>%
  drop_na(Price, Mil, Year, Model, Location)

# --- 3. Build Multiple Linear Regression Model ---
# Y = Price, X = Mil, Year, Model, Location
model <- lm(Price ~ Mil + Year + Model + Location, data = polestar_data)

# Alternative: Model without intercept (shows all Model levels explicitly)
model_no_intercept <- lm(Price ~ 0 + Mil + Year + Model + Location, data = polestar_data)

# --- 4. Results Interpretation (For your Report) ---
# Summary provides Coefficients and P-values for your analysis
summary_result <- summary(model)
print(summary_result)

print("--- Model without intercept (shows all Model coefficients) ---")
summary_no_intercept <- summary(model_no_intercept)
print(summary_no_intercept)

# Calculate RMSE for 'Tabell 1' (Requirement) 
rmse_val <- sqrt(mean(residuals(model)^2))
cat("\n--- Model Evaluation ---\n")
cat("RMSE for the model:", round(rmse_val, 2), "SEK\n")
cat("Adjusted R-squared:", round(summary_result$adj.r.squared, 4), "\n")

# --- 5. Investigation of Theoretical Assumptions (VG REQUIREMENT) ---
# This section generates the plots required by the assignment
par(mfrow = c(2, 2))
plot(model)

# A. Multicollinearity Check (Senior DS approach)
# Checks if Year and Mil are too correlated
cat("\n--- Multicollinearity Check (VIF) ---\n")
print(vif(model))

# B. Confidence Intervals (Added Analysis)
# Shows the range of price impact for 'Mil' with high certainty
cat("\n--- 95% Confidence Intervals ---\n")
print(confint(model, "Mil", level = 0.95))
print(confint(model, "Year", level = 0.95))
print(confint(model, "Model2", level = 0.95))
print(confint(model, "Model3", level = 0.95))
print(confint(model, "Model4", level = 0.95))
print(confint(model, "Location", level = 0.95))