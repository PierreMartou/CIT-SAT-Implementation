require_relative 'constraint'

#
# Class representing an alternative constraint.
# It means that exactly one sub-entity must be active if the current entity is active.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Alternative < Constraint

	def interpret
		return _count_active_children() == 1
	end

	def to_cnf(satSolver)
		cnf_clauses = []

		parent = satSolver.add_literal(@nodes[0].parent.name)
		children = []
		@nodes.each do
			|node|
			children << satSolver.add_literal(node.name)
		end

		# For every child i of children,
		# we add the clauses ( child_i <==> ( Not child_0 & Not child_1 & .... & parent))
		children.each do
			|child|
			_alternative_helper(cnf_clauses, child, children, parent)
		end

		return cnf_clauses
	end

	private

	def _count_active_children()
		counter = 0
		@nodes.each {
				|node|
			if node.can_be_actived?()
				counter += 1
			end
		}
		return counter
	end

	def _alternative_helper(cnf_clauses, current_child, children, parent)
		last_clause = []
		children.each do
			|child|
			last_clause << child
			unless child == current_child
				cnf_clauses << [-current_child, -child]
			end
		end
		cnf_clauses << [-current_child, parent]
		last_clause << -parent
		cnf_clauses << last_clause
	end

end