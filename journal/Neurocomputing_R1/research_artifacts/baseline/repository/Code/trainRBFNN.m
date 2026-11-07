function [centers, weights, sigma] = trainRBFNN(X, Y, numCenters, spread)

    fprintf('  Training RBFNN with %d centers...\n', numCenters);
    
    fprintf('  Selecting centers using k-means...\n');
    centers = selectCentersKMeans(X, numCenters);
    
    if nargin < 4 || isempty(spread)
        sigma = calculateSigma(centers);
    else
        sigma = spread;
    end
    
    fprintf('  Sigma = %.4f\n', sigma);
    
    fprintf('  Computing RBF activations...\n');
    H = computeRBFActivations(X, centers, sigma);
    
    fprintf('  Solving for output weights...\n');
    weights = Y * pinv(H);  % [classes x numCenters]
    
    fprintf('  Training completed!\n');
end

function centers = selectCentersKMeans(X, numCenters)
    [~, centers] = kmeans(X', numCenters, 'MaxIter', 100, 'Display', 'off');
    centers = centers';
end

function sigma = calculateSigma(centers)
    numCenters = size(centers, 2);
    distances = zeros(numCenters);
    
    for i = 1:numCenters
        for j = 1:numCenters
            distances(i,j) = norm(centers(:,i) - centers(:,j));
        end
    end
    
    % Average distance between centers
    avgDist = mean(distances(:));
    sigma = avgDist / sqrt(2 * numCenters);
end

function H = computeRBFActivations(X, centers, sigma)
%% Compute RBF 

    numCenters = size(centers, 2);
    numSamples = size(X, 2);
    H = zeros(numCenters, numSamples);
    
    for i = 1:numCenters
        diff = X - centers(:, i);
        distances = sqrt(sum(diff.^2, 1));
        
        % Gaussian RBF 
        H(i, :) = exp(-distances.^2 / (2 * sigma^2));
    end
end