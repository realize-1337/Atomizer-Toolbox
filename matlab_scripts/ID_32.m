% Funtion zur Berechnung des integralen SMD mittels der Methode nach
% Zhang
% Autor:    AS
% Date:     07.01.2015
% "i" entspricht Messposition (Bsp.: r_1 = 0 mm)

% Übergabegrößen:
% D30_i = D_30_radial;
% D20_i = D_20_radial;
% r_i = r_i;
% n_flux_i = n_flux_radial;
% max_r_i = -44;

function [I_D32] = ID_32(D30_i,D20_i,r_i,n_flux_i,max_r_i)

% Start der Funktion:******************************************************
%D30_i = D30_i';
%D20_i = D20_i';
%r_i = r_i';
%n_flux_i = n_flux_i';

% Max Index finden
if max_r_i < 0
    I_r_i_max = find(r_i < max_r_i);
else
    I_r_i_max = find(r_i > max_r_i);
end

[~, I_r_i_min] = min(abs(r_i));

if abs(r_i(1)) == abs(r_i(end))
    % komplettes Radialprofil gemessen
    % Daten von negativer Profilseite werden genommen
        D20_i = [D20_i(1:I_r_i_min) abs(fliplr(D20_i(1:I_r_i_min-1)))];
        D30_i = [D30_i(1:I_r_i_min) abs(fliplr(D30_i(1:I_r_i_min-1)))];
        n_flux_i = [n_flux_i(1:I_r_i_min) abs(fliplr(n_flux_i(1:I_r_i_min-1)))];
else
    % KEIN komplettes Radialprofil gemessen
    % Prüfen ob positives oder negatives Radialprofil gemessen wurde
    if I_r_i_min > length(r_i)/2 % negatives Radialprofil
        r_i = [r_i(1:I_r_i_min) abs(fliplr(r_i(1:I_r_i_min-1)))];
        D20_i = [D20_i(1:I_r_i_min) abs(fliplr(D20_i(1:I_r_i_min-1)))];
        D30_i = [D30_i(1:I_r_i_min) abs(fliplr(D30_i(1:I_r_i_min-1)))];
        n_flux_i = [n_flux_i(1:I_r_i_min) abs(fliplr(n_flux_i(1:I_r_i_min-1)))];
    else
        % positives Radialprofil
        r_i = [abs(flip(r_i(I_r_i_min+1:end))) r_i(I_r_i_min:end)];
        D20_i = [abs(flip(D20_i(I_r_i_min+1:end))) D20_i(I_r_i_min:end)];
        D30_i = [abs(flip(D30_i(I_r_i_min+1:end))) D30_i(I_r_i_min:end)];
        n_flux_i = [abs(flip(n_flux_i(I_r_i_min+1:end))) n_flux_i(I_r_i_min:end)];      
    end 
end

% Berechnung integraler SMD I_D32 aus ID30 & ID20

r_i_cut = zeros(1,length(r_i));
D32_i = zeros(1,length(r_i));

for i=1:length(D30_i)
    D32_i(i) = D30_i(i)^3/D20_i(i)^2;
    r_i_cut(i) = r_i(i);
end

% D30 zuschneiden auf max zugelassene Radialposition;
D30_i = D30_i(1,(length(I_r_i_max)+1):(length(r_i)-length(I_r_i_max)));
D20_i = D20_i(1,(length(I_r_i_max)+1):(length(r_i)-length(I_r_i_max)));
n_flux_i = n_flux_i(1,(length(I_r_i_max)+1):(length(r_i)-length(I_r_i_max)));
r_i_cut = r_i_cut(1,(length(I_r_i_max)+1):(length(r_i)-length(I_r_i_max)));
D32_i = D32_i(1,(length(I_r_i_max)+1):(length(r_i)-length(I_r_i_max)));

% Kreisringfläche berechnen:

delta_r = zeros(1,length(r_i_cut(r_i_cut <= 0 ))); % [mm]
area_annulus = zeros(1,length(r_i_cut(r_i_cut <=0))); % [mm^2]

for i=1:length(r_i_cut(r_i_cut <= 0 ))
    delta_r(1,i) = abs(r_i_cut(i) - r_i_cut(i+1));  
end

for i=1:length(area_annulus)
    if r_i_cut(i) == 0
        area_annulus(i) = pi*(delta_r(find(r_i_cut == 0))/2)^2;
    else
        area_annulus(i) = pi*((abs(r_i_cut(i))+(delta_r(i)/2))^2 - (abs(r_i_cut(i))-(delta_r(i)/2))^2)/2;
    end
end
area_annulus = [area_annulus fliplr(area_annulus(1:end-1))];% Angabe in mm^2
area_annulus = area_annulus.*10^6;  % Angabe in µm^2

I_D32 = sum(D30_i.^3.*n_flux_i.*area_annulus)/sum(D20_i.^2.*n_flux_i.*area_annulus);



