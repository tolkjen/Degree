@app.task
def evaluate(filepath, random_state, pairs):
    checksum = file_checksum(filepath)
    xls = file_cache.get(filepath)

    scores = []
    splits = get_splits(xls, random_state)
    for pair in pairs:
        pd = pair.preprocessing_descriptor
        for split in splits:
            if not sample_cache.contains(checksum, split, pd):
                training, test = split

                # Training
                training_sample = Sample.from_file(xls, training)
                imputer = pd.impute(training_sample)
                training_sample.impute_nan(imputer)
                training_sample.remove_columns(pd.removed_columns)
                normalizer = training_sample.get_normalizer()
                training_sample.normalize(normalizer, pd.normalized_columns)
                clusterer = pd.cluster(training_sample)
                training_sample.merge(clusterer)

                # Test
                test_sample = Sample.from_file(xls, test)
                test_sample.impute_nan(imputer)
                test_sample.remove_columns(pd.removed_columns)
                test_sample.normalize(normalizer, pd.normalized_columns)
                test_sample.merge(clusterer)

                sample_cache.set(checksum, split, pd, (training_sample, test_sample))
            else:
                training_sample, test_sample = sample_cache.get(checksum, split, pd)

            clf = pair.classification_descriptor.create_classifier(training_sample)
            scores.append(get_scores(clf, training_sample, test_sample))
    return scores