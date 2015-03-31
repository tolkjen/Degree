#!/bin/bash
app='python -m tools.calculate -gs 30 -ws 50 -cg 10'
#app='python mock.py'

classifiers=( 'tree' 'random_forest' 'knn' 'svc_linear' 'extra_trees' )
n_classifiers=${#classifiers[@]}

fix=( 'remove' 'average' )
n_fix=${#fix[@]}

for (( i=0;i<$n_classifiers;i++)); do
  let index=$(( i + 1 ))
  echo ''
  echo '>>>>>>>>>>>>>>>>>>>>>>>>>>'
  echo '>>>' Testing classifier $index/$n_classifiers: ${classifiers[${i}]} 
  echo '>>>>>>>>>>>>>>>>>>>>>>>>>>'

  for (( j=0;j<$n_fix;j++)); do
    echo ''
    echo '~~~~ Fix' ${fix[${j}]}

    echo ''
    echo 'Removing all possible column combinations...'
    $app data.xls ${classifiers[${i}]} --fix ${fix[${j}]} -rc Age,PSA,TNFA,IL6,IL8,VEGF -rs 1,2,3,4,5

    echo ''
    echo 'Normalizing all possible column combinations...'
    $app data.xls ${classifiers[${i}]} --fix ${fix[${j}]} -nc Age,PSA,TNFA,IL6,IL8,VEGF -ns 1,2,3,4,5,6

    echo ''
    echo 'Removing and normalizing all possible column combinations...'
    $app data.xls ${classifiers[${i}]} --fix ${fix[${j}]} -nc Age,PSA,TNFA,IL6,IL8,VEGF -ns 1,2,3,4,5,6 -rc Age,PSA,TNFA,IL6,IL8,VEGF -rs 1,2,3,4,5
  done
done

