knitr::opts_chunk$set(echo = TRUE)

filepath = ""
df <- read_csv(filepath)

calculate_median <- function(x) {
  if (length(x) == 1) {
    return(0)
  } else {
    return(median(x[-length(x)], na.rm = TRUE))
  }
}


calculate_rolling_median <- function(data, column, n) {
  data <- data %>% group_by(Name)
  
  column_name <- paste0("L", n, "_", column)
  
  data <- data %>%
    mutate("{column_name}" := rollapply(.data[[column]], width = (n+1), FUN = calculate_median,
                                        fill = NA, align = "right", partial = TRUE)) %>%
    ungroup()
  
  data <- data %>% group_by(Name, opp)
  
  n_opp <- floor(n/2)
  
  column_name_opp <- paste0("L", n_opp, "_", column,"_opp")
  
  data <- data %>%
    mutate("{column_name_opp}" := rollapply(.data[[column]], width = (n_opp+1), FUN = calculate_median, fill = NA, align = "right",partial=TRUE))
  
  data <- data %>% ungroup()
  
  
  return(data)
}

columns_to_watch <- c("FG", "FGA", "3P", "3PA", "FT", "FTA", "TRB", "AST", "STL", "BLK", "TOV", "PF",
                      "+/-", "TS%", "eFG%", "USG%", "ORtg", "DRtg", "BPM", "PTS")

for (column in columns_to_watch) {
  print(column)
  df <- calculate_rolling_median(df, column, 10)
}

new_filepath <- sub(".csv$", "-wtp.csv", original_filepath)

write.csv(df, file = new_filepath, row.names = FALSE)
