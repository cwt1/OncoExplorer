function [C, L, U] = SpectralClustering(W, k)
%SPECTRALCLUSTERING Executes spectral clustering algorithm
%   Executes the spectral clustering algorithm defined by
%   Type on the adjacency matrix W and returns the k cluster
%   indicator vectors as columns in C.
%   If L and U are also called, the (normalized) Laplacian and
%   eigenvectors will also be returned.
%
%   'W' - Adjacency matrix, needs to be square
%   'k' - Number of clusters to look for
%   Normalized according to Jordan and Weiss (2002)
%   Author: Ingo Buerk
%   Year  : 2011/2012
%   Bachelor Thesis

% calculate degree matrix
degs = sum(W, 2);
D    = sparse(1:size(W, 1), 1:size(W, 2), degs);

% compute unnormalized Laplacian
L = D - W;

% compute normalized Laplacian if needed
% avoid dividing by zero
degs(degs == 0) = eps;
% calculate D^(-1/2)
D = spdiags(1./(degs.^0.5), 0, size(D, 1), size(D, 2));

% calculate normalized Laplacian
L = D * L * D;


% compute the eigenvectors corresponding to the k smallest
% eigenvalues
diff   = eps;
[U, ~] = eigs(L, k, diff);

% in case of the Jordan-Weiss algorithm, we need to normalize
% the eigenvectors row-wise
U = bsxfun(@rdivide, U, sqrt(sum(U.^2, 2)));


% now use the k-means algorithm to cluster U row-wise
% C will be a n-by-1 matrix containing the cluster number for
% each data point
C = kmeans(U, k, 'start', 'cluster', ...
                 'EmptyAction', 'singleton');

% now convert C to a n-by-k matrix containing the k indicator
% vectors as columns
C = sparse(1:size(D, 1), C, 1);

end