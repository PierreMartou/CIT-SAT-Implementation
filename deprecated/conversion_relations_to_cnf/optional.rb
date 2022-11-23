require_relative 'constraint'

#
# Class representing an optional constraint.
# It means that the sub-entity may be active or not.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Optional < Constraint

	def interpret()
		return true
	end

	def to_cnf(satSolver)
		cnf_clauses = []
		@nodes.each do
			|node|
			child = satSolver.add_literal(node.name)
			parent = satSolver.add_literal(node.parent.name)
			cnf_clauses << [-child, parent]
		end
		return cnf_clauses
	end

end