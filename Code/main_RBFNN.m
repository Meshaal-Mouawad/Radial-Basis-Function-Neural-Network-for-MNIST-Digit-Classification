

clear; clc; close all;

fprintf('STEP 1: Loading MNIST dataset...\n');
trainData = load('MNIST_train.mat');
trainImages = trainData.imagestrain;      % 28x28x60000
trainLabels = trainData.labelstrain;      % 60000x1
testData = load('MNIST_test.mat');
testImages = testData.images;             % 28x28x10000
testLabels = testData.labels;             % 10000x1

fprintf('  [OK] Training data: %d images\n', size(trainImages, 3));
fprintf('  [OK] Test data: %d images\n\n', size(testImages, 3));

fprintf('STEP 2: Preprocessing data...\n');

% Reshape images
allTrainImages = reshape(trainImages, 28*28, size(trainImages, 3)) / 255;
allTestImages = reshape(testImages, 28*28, size(testImages, 3)) / 255;

% Convet labels
trainLabelsOneHot = full(ind2vec(trainLabels' + 1));
testLabelsOneHot = full(ind2vec(testLabels' + 1));

% keep original
trainLabelsOrig = trainLabels;
testLabelsOrig = testLabels;

fprintf('  [OK] Training data: %d samples, %d features\n', size(allTrainImages, 2), size(allTrainImages, 1));
fprintf('  [OK] Test data: %d samples, %d features\n\n', size(allTestImages, 2), size(allTestImages, 1));

fprintf('STEP 3: Selecting training subset...\n');

useSubset = true;  % Set to false to use all 60,000 samples
%subsetSize = 10000;  % Number of training samples to use
subsetSize = 20000; % increased frpm 10k to 2k

if useSubset
    rng(42);  % For reproducibility
    indices = randperm(size(allTrainImages, 2), subsetSize);
    X_train = allTrainImages(:, indices);
    Y_train = trainLabelsOneHot(:, indices);
    Y_train_orig = trainLabelsOrig(indices);
    fprintf('  [OK] Using subset: %d training samples\n', subsetSize);
else
    X_train = allTrainImages;
    Y_train = trainLabelsOneHot;
    Y_train_orig = trainLabelsOrig;
    fprintf('  [OK] Using all %d training samples\n', size(X_train, 2));
end

X_test = allTestImages;
Y_test = testLabelsOneHot;
Y_test_orig = testLabelsOrig;

fprintf('  [OK] Training features: %d x %d\n', size(X_train, 1), size(X_train, 2));
fprintf('  [OK] Test features: %d x %d\n\n', size(X_test, 1), size(X_test, 2));

fprintf('STEP 4: Training RBF Neural Network...\n');

% RBF Network params
numCenters = 100;        % Number of RBF centers (hidden layer neurons)
spread = 1.0;           % Spread parameter for RBF (sigma)


[centers, weights, sigma] = trainRBFNN(X_train, Y_train, numCenters, spread);

fprintf('  [OK] RBF Network trained with %d centers\n', numCenters);
fprintf('  [OK] Output weights dimension: %d x %d\n\n', size(weights, 1), size(weights, 2));

fprintf('STEP 5: Testing RBF Neural Network...\n');

predictions = predictRBFNN(X_test, centers, weights, sigma);

[~, predLabels] = max(predictions, [], 1);
predLabels = predLabels' - 1;  % Convert back to 0-9

accuracy = sum(predLabels == Y_test_orig) / length(Y_test_orig) * 100;

fprintf('  [OK] Test accuracy: %.2f%%\n\n', accuracy);

fprintf('STEP 6: Displaying results...\n');

figure;
confusionchart(Y_test_orig, predLabels, 'Title', 'Confusion Matrix - RBFNN on MNIST');
xlabel('Predicted Label');
ylabel('True Label');

numSamples = 10;
figure;
for i = 1:numSamples
    subplot(2, 5, i);
    img = reshape(X_test(:, i), 28, 28);
    imshow(img, []);
    title(sprintf('True: %d, Pred: %d', Y_test_orig(i), predLabels(i)));
end
sgtitle('Sample Predictions on MNIST Test Set');

% Calculate per-cals accuracy
fprintf('\nPer-class accuracy:\n');
for class = 0:9
    idx = (Y_test_orig == class);
    class_acc = sum(predLabels(idx) == class) / sum(idx) * 100;
    fprintf('  Digit %d: %.2f%%\n', class, class_acc);
end