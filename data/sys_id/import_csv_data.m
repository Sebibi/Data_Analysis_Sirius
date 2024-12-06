file_name = 'linear_torque_full_processed.csv';
raw_data = readmatrix(file_name);
raw_data = raw_data(2:end, :);

dt = 0.01;
% time = raw_data(:, 1);
u = raw_data(:, 1:4);
y = raw_data(:, 5:end);
data_linear = iddata(y, u, 0.01);

file_name = 'step_torque_full_processed.csv';
raw_data = readmatrix(file_name);
raw_data = raw_data(2:end, :);

dt = 0.01;
% time = raw_data(:, 1);
u = raw_data(:, 1:4);
y = raw_data(:, 5:end);
data_step = iddata(y, u, 0.01);

% rpm_to_rad_s = 2*pi / (60 * 13.188);
% tfss = [tf1, tf2, tf3, tf4];
% 
% Inertias = [0, 0, 0, 0];
% ks = [0, 0, 0, 0];

% 
% for i=1:4
%     nom = tfss(i).Numerator * rpm_to_rad_s;
%     denom = tfss(i).Denominator;
% 
%     Inertias(i) = denom(1) / nom;
%     ks(i) = denom(2) / nom;
% end
% 
% Inertias
% ks






