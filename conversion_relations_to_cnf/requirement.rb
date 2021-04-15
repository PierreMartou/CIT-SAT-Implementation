require_relative 'dependency'

#
# Class representing a requirement dependency.
# It means that the source entity can be active if and only if the target entity is active.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Requirement < Dependency

	def interpret()
		target_satisfied = true
		@nodes.each { 
			|node|  
			target_satisfied &&= node.can_be_actived?()
		}
		return target_satisfied
	end

	def to_cnf (satSolver)
		cnf_clauses = []
		@nodes.each do
			|node|
			target = satSolver.add_literal(node.name)
			source = satSolver.add_literal(self.source.name)
			cnf_clauses << [-source, target]
		end
		return cnf_clauses
	end

end