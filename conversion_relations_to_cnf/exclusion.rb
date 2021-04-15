require_relative 'dependency'

#
# Class representing an exclusion dependency.
# It means that the entities are mutual exclusive, i.e. they cannot be active in the same time.
#
# Author: Benoît Duhoux
# Date: 2018
#
class Exclusion < Dependency

	def interpret()
		# Assumption: @nodes is not empty otherwise the dependency would not be created
		target_satisfied = true
		@nodes.each { 
			|node|  
			target_satisfied &&= node.can_be_actived?()
		}
		return @source.can_be_actived?() ^ target_satisfied
	end

	def to_cnf(satSolver)
		cnf_clauses = []
		@nodes.each do
			|node|
			target = satSolver.add_literal(node.name)
			source = satSolver.add_literal(self.source.name)
			cnf_clauses << [-target, -source]
		end
		return cnf_clauses
	end

end