# CQA for primary keys Datalog Rewriter
## Introduction
This is a Python 3.X script that generates a Datalog program for the problem know in the litterature as CQA.
By default, it takes as input a file containing a sjfBCQ query and writes the output program in a file named "output.txt", but the main.py file can be easily modified to change this behavior.
## References
* \[1\] Jef Wijsen, Paraschos Koutris.  Consistent query answering for primarykeys in datalog.  2019.
* \[2\] Jef Wijsen, Paraschos Koutris.  Consistent query answering for self-join-free conjunctive queries under primary key constraints.  2017.
* \[3\] Jef Wijsen. Certain conjuctive query answering in first-order logic. 2012.
## What is a CQA Problem?
**CQA** for primary keys is the following problem:

Given a database **db** that may violate its primary-key constraints, multiple reparations can be generated by deleting a minimal set of tuples from **db**. 
For every sjfCBQ **q**, **CERTAINTY(q)** is the problem that takes as input **db** and asks whether **q** evaluates true for every reparation of **db**.

This scripts impliments **CERTAINTY(q)** in a **Datalog** program.
## Usage
The main script takes as input a sjfBCQ using a specific syntax.
The syntax is essentially the same than Datalog rules, but extending it with key-values being surrounded by [ ]

Example : R(\[X\],Y),S(\[Y\],X) is a valid query.
## How does it work?
The articles in the References section talk about how the complexity of **CERTAINTY(q)** can be determined. 
This code generates all the necessary tools (Attack Graph) to find the complexity of **CERTAINTY(q)**.
As it is specified in the articles, there're 3 cases:

* **CERTAINTY(Q)** is in **FO**
* **CERTAINTY(Q)** is in **L**
* **CERTAINTY(Q)** is in **Co-NPHard**

For the 2 first cases, a Datalog rewrite is possible. The third case can be detected but a rewriting is not possible.

### Saturated query
The following process suppose that q is saturated. In [1], there's a proof that for every sjfBCQ **q**, a sjfBCQ **q'** such that:

* **CERTAINTY(q)** = **CERTAINTY(q')**
* **q'** is saturated
* the redcution from **q** to **q'** is in FO.

This process of saturation is implemented by checking if q is saturated and, if it is not, adding a set of rules at the start of the Datalog program that ensures that **q** is saturated.

### Rewriting an unattacked atom
We say that an atom A is unattacked if for every atom B, there isn't an edge B->A in the attack graph.
Theory tells us that in that case, this atom can be rewrited in FO. \[3\] gives us this formula :

![f1]

Where :
* ![v] is the sequence of variables appearing in R.
* C is a set of equalities initially empty.
* ![z] is a vector with the same size of ![y] which is constructed in the following way for every ![yi] in ![y]:
	* if:
		* ![yi] appears in ![x]
		* ![yi] is a constant
		* for some j < i, ![yi] = ![yj]
	* then ![zi] is a fresh variable and C contains  ![zi] = ![yi]
	* else, ![zi] = ![yi]
* ![phi] is the rewriting of **q'**=**q** \ {R(![x], ![y])} where all the variables of ![v] become constants.

Unformally, this formula searches for blocks of key-equal facts where every fact of the block verifies **q'**.

To make easier the Datalog rewrite, i use 2 supplementary vectors ![z1] and ![z2] that are constructed in the following way for every ![yi] in ![y]:

* if:
	* ![yi] appears in ![x]
	* ![yi] is a constant
	* for some j < i, ![yi] = ![yj]
* then ![z2] contains ![zi] 
* else, ![z1] contains ![zi]


A Datalog rewriting of this formula:

```
R_0 :- R(X,Y), not R_1(X)
R_1(X) :- R(X,Z), not R_2(X,Z1,Z2)
R_2(X,Y,Z2) :- R(X,Z'), C, R_3(X,Y)
```

Where :
* X,Y,Z,Z1,Z2 take the values from vectors ![x], ![y], ![z], ![z1], ![z2]
* Z' is the vector Z where:
	* if ![zi] is in ![z1]
	* then ![zi] = ![yi]
		
* R_3 is the rewriting of **q'**=**q** \ {R(![x], ![y])}.



As you notice, this only requires the compute of ![v], ![z] and C! 

### Rewriting a weak cycle
In this section i use notions like **Strong cycles**, **M-Graph**,**![m] -Graph**, **Block-Quotient Graph**, **1-embedding**, etc...

To know the meaning of these notions, please give a look to **\[1\]**.

Theory says that **CERTAINTY(q)** is in **L** if and only if the **Attack Graph** of q contains no strong cycle. 

The detection of cycles can be done with classic cycle detection algorithms. Checking if a cycle is strong can also be done in polynomial time.

Once we're sure that there's no strong cycle, we have to rewrite the weak ones. 

Let C be the cycle to be removed. Theory shows us a method based in the removal of **Garbage-sets** :  facts that do not affect the result of **CERTAINTY(q)**.

The code generates necessary tools (M-Graph) and a set of Datalog rules that keep the facts that do not belong to a **Garbag-Set** :

* **Relevant_Ri** rules to find the facts Ri that do belong to a relevant **1-embedding**.
* **Pk** rule that verify the existence of a directed path in the block-quotient graph.
* **Dcon** rules that veryfies the existence of a direct path between 2 blocks in the block-quotient graph without using a set of banned blocks.
* **InLongDCycle** rule that finds cycles in the block-quotient graph.
* **Garbage_Ri** rules that finds the facts Ri belonging to a garbage set.
* **Keep_Ri** rules that keeps the fact Ri that do not belong to a garbage set.

Indeed, the removal of this **Garbage-set** will keep only a set of relevant **1-embeddings** that can be encoded by a fresh relation T(![u], ![w]) where Vars(![w]) = Vars(C) and **u** is a fresh variable that is used as identifier for every strong component in the ![m] graph.

After that, we can study the query **q'** = (**q** \ C) U {T} U p where p is a set of relations ![ni] for every relation ![fi] in C.

The creation of these relations is made by adding Datalog rules.

The sub-query {T} U p contains no cycle and,thus, we can apply the first method.

### Main Algorithm
```
if q is not saturated:
	q = saturate(q)
a = Attack Graph of q
if a do not contain any strong cycle:
	while a is not empty:
		for unattacked vertex in a:
			rewrite unattacked vertex using FO logic
		if a is not empty:
			rewrite a cycle in the M-Graph using L logic
												

```

[f1]: http://chart.apis.google.com/chart?cht=tx&chl=\exists\vec{v},R(\underline{\vec{x}},\vec{y})\wedge\forall\vec{z}(R(\underline{\vec{x}},\vec{z})\rightarrow(C\wedge\phi(\vec{v})))  

[x]: http://chart.apis.google.com/chart?cht=tx&chl=\underline{\vec{x}}
[y]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{y}
[yi]: http://chart.apis.google.com/chart?cht=tx&chl=y_i 
[yj]: http://chart.apis.google.com/chart?cht=tx&chl=y_j 
[v]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{v} 
[z]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{z} 
[zi]: http://chart.apis.google.com/chart?cht=tx&chl=z_i 
[z1]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{z_1} 
[z2]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{z_2} 
[phi]: http://chart.apis.google.com/chart?cht=tx&chl=\phi(\vec{v}) 
[u]: http://chart.apis.google.com/chart?cht=tx&chl=\underline{u} 
[w]: http://chart.apis.google.com/chart?cht=tx&chl=\vec{w} 
[m]: https://chart.apis.google.com/chart?cht=tx&chl=\rightarrow^C
[ni]: https://chart.apis.google.com/chart?cht=tx&chl=N_i^c(\underline{Key(F_i)},u)
[fi]: https://chart.apis.google.com/chart?cht=tx&chl=F_i





