function predictions = predictRBFNN(X, centers, weights, sigma)


    H = computeRBFActivations(X, centers, sigma);
    
    % Compute output predictions
    predictions = weights * H;
end

function H = computeRBFActivations(X, centers, sigma)
    numCenters = size(centers, 2);
    numSamples = size(X, 2);
    H = zeros(numCenters, numSamples);
    
    for i = 1:numCenters
        diff = X - centers(:, i);
        distances = sqrt(sum(diff.^2, 1));
        H(i, :) = exp(-distances.^2 / (2 * sigma^2));
    end
end