import featuretools as ft
import pytest

from composeml import LabelMaker


def total_spent(df):
    total = df.amount.sum()
    return total


@pytest.fixture
def labels():
    df = ft.demo.load_mock_customer(return_single_table=True, random_seed=0)

    lm = LabelMaker(
        target_entity='customer_id',
        time_index='transaction_time',
        labeling_function=total_spent,
        window_size='1h',
    )

    lt = lm.search(
        df[['transaction_time', 'customer_id', 'amount']],
        minimum_data='10min',
        num_examples_per_instance=2,
        gap='30min',
        verbose=False,
    )

    lt = lt.threshold(1250)
    return lt


def test_dfs(labels):
    es = ft.demo.load_mock_customer(return_entityset=True, random_seed=0)
    feature_matrix, _ = ft.dfs(entityset=es, target_entity='customers', cutoff_time=labels, cutoff_time_in_index=True)
    assert labels.name in feature_matrix

    columns = ['customer_id', 'time', labels.name]
    given_labels = feature_matrix.reset_index()[columns]
    given_labels = given_labels.rename(columns={'time': 'cutoff_time'})
    given_labels = given_labels.sort_values(['customer_id', 'cutoff_time'])
    given_labels = given_labels.reset_index(drop=True)
    given_labels = given_labels.rename_axis('label_id')

    assert given_labels.equals(labels)
