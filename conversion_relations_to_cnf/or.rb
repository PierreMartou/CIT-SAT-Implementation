require_relative 'constraint'

#
# Class representing an or constraint.
# It means that at least one sub-entity must be active if the current entity is active.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Or < Constraint

	def interpret()
		satisfied = false
		@nodes.each { 
			|node|  
			satisfied ||= node.can_be_actived?()
		}
		return satisfied
	end

	def to_cnf (satSolver)
		cnf_clauses = []
		parent = satSolver.add_literal(@nodes[0].parent.name)
		final_clause = [-parent]
		@nodes.each do
			|node|
			child = satSolver.add_literal(node.name)
			cnf_clauses << [-child, parent]
			final_clause << child
		end
		cnf_clauses << final_clause
		return cnf_clauses
	end

end