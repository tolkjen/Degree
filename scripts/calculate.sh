#!/bin/bash
app='python -m tools.validate -gs 30 -ws 50 -cg 10'
#app='python mock.py'

classifiers=( 'tree' 'random_forest' 'svc_rbf' 'knn' 'svc_linear' 'extra_trees' )
n_classifiers=${#classifiers[@]}

for (( i=0;i<$n_classifiers;i++)); do
  let index=$(( i + 1 ))
	echo ''
	echo '>>>>>>>>>>>>>>>>>>>>>>>>>>'
	echo '>>>' Testing classifier $index/$n_classifiers: ${classifiers[${i}]} 
	echo '>>>>>>>>>>>>>>>>>>>>>>>>>>'

	echo ''
  echo 'Different fix methods...'
	$app data.xls ${classifiers[${i}]} --fix remove,average

	echo ''
  echo 'Removing all possible column combinations...'
	$app data.xls ${classifiers[${i}]} --fix remove -rc Age,PSA,TNFA,IL6,IL8,VEGF -rs 1,2,3,4,5

	echo ''
  echo 'Normalizing all possible column combinations...'
	$app data.xls ${classifiers[${i}]} --fix remove -nc Age,PSA,TNFA,IL6,IL8,VEGF -ns 1,2,3,4,5,6

	echo ''
  echo 'Removing and normalizing all possible column combinations...'
	$app data.xls ${classifiers[${i}]} --fix remove -nc Age,PSA,TNFA,IL6,IL8,VEGF -ns 1,2,3,4,5,6 -rc Age,PSA,TNFA,IL6,IL8,VEGF -rs 1,2,3,4,5
done

