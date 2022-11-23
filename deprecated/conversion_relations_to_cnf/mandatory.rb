+require_relative 'constraint'

#
# Class representing a mandatory constraint.
# It means that the sub-entity must be active.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Mandatory < Constraint

	def interpret()
		satisfied = true
		@nodes.each { 
			|node|  
			satisfied &&= node.can_be_actived?()
		}
		return satisfied
	end

	def sub_relations()
		sub_relations = []
		@nodes.each { 
			|node|  
			sub_relations += node.relations.values()
		}
		return sub_relations
	end

	def to_cnf(satSolver)
		cnf_clauses = []
		@nodes.each do
			|node|
			child = satSolver.add_literal(node.name)
			parent = satSolver.add_literal(node.parent.name)
			cnf_clauses << [child, -parent] << [-child, parent]
		end
		return cnf_clauses
	end

end