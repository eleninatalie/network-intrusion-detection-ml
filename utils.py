"""
Utility Functions for UNSW-NB15 Cybersecurity Classification
Shared functions for data loading, preprocessing, and model evaluation
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score
)


def load_unsw_data(train_file="UNSW_NB15_train_LEAKAGE_REMOVED.csv",
                   test_file="UNSW_NB15_test_LEAKAGE_REMOVED.csv"):
    """
    Load UNSW_NB15_LEAKAGE_REMOVED datasets.
    
    Parameters:
    -----------
    train_file : str
        Path to training CSV file
    test_file : str
        Path to test CSV file
    
    Returns:
    --------
    tuple: (train_data, test_data, combined_df)
        - train_data: Training set DataFrame
        - test_data: Test set DataFrame
        - combined_df: Combined train + test DataFrame
    """
    try:
        train_data = pd.read_csv(train_file)
        test_data = pd.read_csv(test_file)
        
        print("="*80)
        print("DATA LOADING SUCCESSFUL")
        print("="*80)
        print(f"\nTrain Set: {train_data.shape[0]:,} samples x {train_data.shape[1]} features")
        print(f"Test Set:  {test_data.shape[0]:,} samples x {test_data.shape[1]} features")
        
        # Combine for overview
        df = pd.concat([train_data, test_data], ignore_index=True)
        print(f"Combined:  {df.shape[0]:,} samples x {df.shape[1]} features\n")
        
        return train_data, test_data, df
    
    except FileNotFoundError as e:
        print(f"ERROR: Could not load datasets: {e}")
        raise


def get_raw_network_features():
    """
    Return list of 25 raw network feature indices (no leakage features).
    
    Returns:
    --------
    list: Feature indices as strings for accessing DataFrame columns
    """
    return [
        '5', '6', '7', '8',                    # bytes_sent, bytes_received, packets_sent, packets_received
        '10', '11',                             # ttl_sender, ttl_receiver
        '12', '13',                             # sender_data_load, receiver_data_load
        '14', '15',                             # packets_lost_sender, packets_lost_receiver
        '16', '17',                             # time_between_sender_packets, time_between_receiver_packets
        '18', '19',                             # jitter_sender, jitter_receiver
        '20', '21', '22', '23',                # tcp_window_sender, tcp_sequence_sender, tcp_sequence_receiver, tcp_window_receiver
        '24', '25', '26',                      # tcp_round_trip_time, tcp_syn_ack_time, tcp_ack_data_time
        '27', '28',                             # mean_packet_size_sender, mean_packet_size_receiver
        '29', '30'                              # http_transaction_depth, server_response_size
    ]


def get_feature_mapping():
    """
    Return mapping dictionary of feature indices to readable names.
    
    Returns:
    --------
    dict: Mapping of feature indices (as strings) to readable names
    """
    return {
        '5': 'bytes_sent',
        '6': 'bytes_received',
        '7': 'packets_sent',
        '8': 'packets_received',
        '10': 'ttl_sender',
        '11': 'ttl_receiver',
        '12': 'sender_data_load',
        '13': 'receiver_data_load',
        '14': 'packets_lost_sender',
        '15': 'packets_lost_receiver',
        '16': 'time_between_sender_packets',
        '17': 'time_between_receiver_packets',
        '18': 'jitter_sender',
        '19': 'jitter_receiver',
        '20': 'tcp_window_sender',
        '21': 'tcp_sequence_sender',
        '22': 'tcp_sequence_receiver',
        '23': 'tcp_window_receiver',
        '24': 'tcp_round_trip_time',
        '25': 'tcp_syn_ack_time',
        '26': 'tcp_ack_data_time',
        '27': 'mean_packet_size_sender',
        '28': 'mean_packet_size_receiver',
        '29': 'http_transaction_depth',
        '30': 'server_response_size'
    }


def prepare_train_test_split(df, train_data, raw_network_features=['5', '6', '7', '8']):
    """
    Prepare train/test split preserving original dataset boundaries.
    Features must already be selected before calling this function.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Combined dataset with selected features
    train_data : pd.DataFrame
        Original training data (used to determine split point)
    raw_network_features : list
        List of feature columns (default: raw network features)
    
    Returns:
    --------
    tuple: (X_train, X_test, y_train, y_test)
        Feature matrices and target vectors
    """
    X = df.drop('is_attack', axis=1)
    y = df['is_attack']
    
    n_train = len(train_data)
    
    X_train = X.iloc[:n_train].reset_index(drop=True)
    y_train = y.iloc[:n_train].reset_index(drop=True)
    X_test = X.iloc[n_train:].reset_index(drop=True)
    y_test = y.iloc[n_train:].reset_index(drop=True)
    
    print("="*80)
    print("TRAIN/TEST SPLIT (Using Original Dataset Boundaries)")
    print("="*80)
    print(f"\nTrain Set: {X_train.shape[0]:,} samples")
    print(f"   Normal (0): {(y_train==0).sum():,} ({(y_train==0).sum()/len(y_train)*100:.1f}%)")
    print(f"   Attack (1): {(y_train==1).sum():,} ({(y_train==1).sum()/len(y_train)*100:.1f}%)")
    
    print(f"\nTest Set: {X_test.shape[0]:,} samples")
    print(f"   Normal (0): {(y_test==0).sum():,} ({(y_test==0).sum()/len(y_test)*100:.1f}%)")
    print(f"   Attack (1): {(y_test==1).sum():,} ({(y_test==1).sum()/len(y_test)*100:.1f}%)\n")
    
    return X_train, X_test, y_train, y_test


def evaluate_binary_classifier(y_test, y_pred, y_proba, model_name="Model", verbose=True):
    """
    Standard evaluation metrics for binary classification.
    
    Parameters:
    -----------
    y_test : array-like
        True test labels
    y_pred : array-like
        Predicted labels
    y_proba : array-like
        Predicted probabilities for positive class
    model_name : str
        Name of the model (for display purposes)
    verbose : bool
        Whether to print detailed output
    
    Returns:
    --------
    dict: Dictionary with all calculated metrics
        Keys: accuracy, precision, recall, f1, auc_roc, confusion_matrix, etc.
    """
    # Calculate metrics
    test_acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc_roc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    metrics = {
        'accuracy': test_acc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc_roc': auc_roc,
        'specificity': specificity,
        'sensitivity': sensitivity,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'tp': tp,
        'confusion_matrix': cm
    }
    
    if verbose:
        print("="*80)
        print(f"MODEL EVALUATION: {model_name}".upper())
        print("="*80)
        
        print(f"\nACCURACY:")
        print(f"   Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
        
        print(f"\nCLASSIFICATION METRICS:")
        print(f"   Precision: {precision:.4f} (False Alarm Rate: {(1-precision)*100:.2f}%)")
        print(f"   Recall:    {recall:.4f} (Attack Detection Rate: {recall*100:.2f}%)")
        print(f"   F1-Score:  {f1:.4f}")
        print(f"   AUC-ROC:   {auc_roc:.4f}")
        
        print(f"\nCONFUSION MATRIX:")
        print(f"   True Negatives:  {tn:,}")
        print(f"   False Positives: {fp:,}")
        print(f"   False Negatives: {fn:,}")
        print(f"   True Positives:  {tp:,}")
        
        print(f"\nDERIVED METRICS:")
        print(f"   Specificity (TNR): {specificity:.4f}")
        print(f"   Sensitivity (TPR): {sensitivity:.4f}")
        
        print(f"\nCLASSIFICATION REPORT:")
        print(classification_report(y_test, y_pred, target_names=['Normal (0)', 'Attack (1)'], zero_division=0))
    
    return metrics


def compare_models(models_dict):
    """
    Compare performance metrics across multiple models.
    
    Parameters:
    -----------
    models_dict : dict
        Dictionary with model names as keys and metrics dictionaries as values
        (output from evaluate_binary_classifier)
    
    Returns:
    --------
    pd.DataFrame: Comparison table with metrics for all models
    """
    comparison_data = []
    
    for model_name, metrics in models_dict.items():
        comparison_data.append({
            'Model': model_name,
            'Accuracy': metrics['accuracy'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'F1-Score': metrics['f1'],
            'AUC-ROC': metrics['auc_roc']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    print("\n" + "="*80)
    print("MODEL COMPARISON")
    print("="*80)
    print(comparison_df.to_string(index=False))
    print("="*80 + "\n")
    
    return comparison_df
