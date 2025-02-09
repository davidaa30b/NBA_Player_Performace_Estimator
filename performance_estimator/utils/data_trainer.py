from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold
import pandas as pd
import numpy as np


def get_weights(y_train):
    n = len(y_train)
    weights = np.linspace(0.5, 10, n) 
    return weights

def clean_features(X_train,variance_threshold=0.01,correlation_threshold= 0.9):
    selector = VarianceThreshold(variance_threshold)
    selector.fit(X_train)  
    X_train_cleaned = X_train.loc[:, selector.get_support()]  # Use loc instead of iloc to keep index

    corr_matrix = X_train_cleaned.corr()
    threshold = correlation_threshold
    drop_columns = set()

    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                colname = corr_matrix.columns[i]
                drop_columns.add(colname)

    X_train_cleaned = X_train_cleaned.drop(columns=drop_columns, errors="ignore")

    return X_train_cleaned

def train_random_forest(X_train_cleaned, y_train,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion):
    model = RandomForestRegressor(
        n_estimators=n_trees_forest,        
        max_depth=max_depth_tree,           
        min_samples_split=min_samples_split,      
        min_samples_leaf=min_samples_leaf,       
        random_state=42,           
        criterion=criterion      
    )

    model.fit(X_train_cleaned, y_train)

    importances = model.feature_importances_
    
    feature_importances = pd.DataFrame({
        'Feature': X_train_cleaned.columns,
        'Importance': importances
    })
    
    return model, feature_importances

def select_important_features(X_train_cleaned, feature_importances, threshold=0.01):
    important_features = feature_importances[feature_importances['Importance'] > threshold]
    selected_features = important_features['Feature']
    
    X_train_cleaned_selected = X_train_cleaned[selected_features]
    
    return X_train_cleaned_selected

def data_cleasing(X_train,y_train,df_test_model,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion,variance_threshold,correlation_threshold ):

    X_train_cleaned = clean_features(X_train,variance_threshold,correlation_threshold)

    model, feature_importances = train_random_forest(X_train_cleaned, y_train,n_trees_forest,max_depth_tree,min_samples_split,min_samples_leaf,criterion)
    X_train_cleaned = select_important_features(X_train_cleaned, feature_importances)
    df_test_model_cleaned = df_test_model[X_train_cleaned.columns]

    return  model,X_train_cleaned,df_test_model_cleaned

