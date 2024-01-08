import os

D_A_FOR_PY = '''
    % Funtion zur Berechnung des Messvolumendurchmessers als Funtion der
    % Partikeltrajektorie und der Tropfengr��e unter der Ber�cksichtigung einer
    % Korrelation zwischen Burstl�nge und Tropfengr��e
    % Autor:    AS
    % Editor for Python implementation: David Maerker
    
    
    function [] = D_A_for_py(D, Ttime, LDA1, LDA4, f_1, f_2, ls_p, phi, path)
    
    % Einstellgr��en f�r USER innerhalb der Funktion***************************
    % diese Einstellungen gelten als Standardeinstellungen (erprobt)
    
    bingroesse = 5; %Gr��e eines bins angeben in �m
    bincount = 200; % min Tropfen / Bin f�r Fit (POW- & LOG - Fit) 
    
    % ENDE USER Einstellungen *************************************************
    
    % Start Funktion **********************************************************
    D = D';
    Ttime = Ttime';
    LDA1 = LDA1';
    LDA4 = LDA4';
    
    burst_length = Ttime.*sqrt(LDA1.^2 + LDA4.^2); %Berechnung Burst lenght nach L=Delta_t*Wurzel(u�+v�) in [�m]
    Data_new = [D,Ttime,LDA1,LDA4,burst_length]; %Matrix mit den erforderlichen Daten

    edges=0:bingroesse:(max(ceil(D))+bingroesse); % Bereitstellen der bins  
    
    Data_new_sort = sortrows(Data_new); %Daten nach Durchmesser sortieren

    [N,edges] = histcounts(Data_new_sort(:,1),edges);
    Data_bin = cell(length(N),1);% Zellvektor f�r einzelnen Bin
    count=N(1); %Start count
    Data_bin(1,1)={Data_new_sort(1:count,:)}; %Erste Zelle
    
    for i=2:length(N)
        Data_bin(i,1) = {Data_new_sort((count+1):(count+N(i)),:)}; %Zelle i mit Matrix f�r Bereich beschreiben
        count=count+N(i);
    end
    
    
    % Variablendekleration:
    
    mean_burstlength = zeros(1,length(N));
    mean_burstlengthsquared = zeros(1,length(N));
    
    for i=1:length(N)
        % Berechnung Burstlenght (Burstlength^2) pro Bin
        mean_burstlength(i) = mean(Data_bin{i,1}(:,5));
        mean_burstlengthsquared(i) = mean_burstlength(i).^2; %F�r plot
    end
    
    edges_middle = edges(1,1:end-1) + (bingroesse / 2);
    
    fit_x = edges_middle(~isnan(mean_burstlengthsquared));
    fit_y = mean_burstlengthsquared(~isnan(mean_burstlengthsquared));
    anz_pro_bin = N';
    anz_pro_bin = anz_pro_bin(~isnan(mean_burstlengthsquared));
    
    % Abfangen wenn nicht mindestens 2 Bin`s mehr als bincount Tropfen haben
    sort_anz_pro_bin = sort(anz_pro_bin);
    if sort_anz_pro_bin(numel(sort_anz_pro_bin)-1) < bincount
        bincount = mean(anz_pro_bin);
    end
    
    fit_x = fit_x(anz_pro_bin >= bincount);
    fit_y = fit_y(anz_pro_bin >= bincount);
    
    % Power-Fit f�r geringen Tropfenr��enbereich (d_tr mit Anz > bincount):
    
    %% Fit: 'untitled fit 1'.
    [xData, yData] = prepareCurveData(fit_x, fit_y );
    
    % Set up fittype and options.
    ft = fittype( 'power1' );
    opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
    opts.Display = 'Off';
    opts.StartPoint = [19880.700336885 0.401023878366104];
    
    % Fit model to data.
    [fitresult, gof] = fit(xData, yData, ft, opts);
    
    pow_fitvalues = coeffvalues(fitresult);
    pow_A = pow_fitvalues(1); 
    pow_B = pow_fitvalues(2); 
    
    % Log-Fit f�r gro�en Tropfenr��enbereich (d_tr mit Anz < bincount):
    
    [xData, yData] = prepareCurveData( fit_x, fit_y );
    
    % Set up fittype and options.
    ft = fittype( 'A*log(x)+B', 'independent', 'x', 'dependent', 'y' );
    opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
    opts.Display = 'Off';
    opts.StartPoint = [0.754686681982361 0.276025076998578];
    
    % Fit model to data.
    [fitresult, gof] = fit( xData, yData, ft, opts );
    
    Log_fitvalues = coeffvalues(fitresult);
    Log_A = Log_fitvalues(1); 
    Log_B = Log_fitvalues(2);
    
    x = 0:1:ceil(max(D));
    y_power = pow_A*x.^pow_B;
    y_log = Log_A*log(x)+Log_B;
    
    % max. Tropfendurchmesser festlegen ab dem zwischen Pow - Fit und Log - Fit
    % unterschieden wird
    y_diff = abs(y_log-y_power);
    [kkk, I] = sort(y_diff);
    x_pow_max = max(x(I(1:5)));
    
    % Berechnung des Messvolumendurchmessers D_e als Funktion der Tropfenr��e
    % und der Partikeltrajektorie LDA1 und LDA 2 nach Gleichung 12.48 in
    % Albrecht et.al 
    
    beta = -f_2/f_1;
    ls_korr = ls_p/abs(beta);        %[�m]
    D_val = zeros(length(D),1);   %[�m]
    A_val = zeros(length(D),1);   %[�m^2]

    
    for i=1:length(D)
        if D(i) < x_pow_max
            D_val(i) = (4/pi)*((ls_korr*(sqrt(pow_A*D(i).^pow_B)))/(ls_korr-cos(phi)*sqrt(pow_A*D(i).^pow_B)*abs(LDA4(i)/sqrt(LDA1(i)^2+LDA4(i)^2)))); % [�m]
        else
            D_val(i) = (4/pi)*((ls_korr*(sqrt(Log_A*log(D(i))+Log_B)))/(ls_korr-cos(phi)*sqrt(Log_A*log(D(i))+Log_B)*abs(LDA4(i)/sqrt(LDA1(i)^2+LDA4(i)^2)))); % [�m]   
        end
        
    end
    
    % Ab hier ist D_e in [�m]
    
    for i=1:length(D)
       A_val(i) = (D_val(i)*ls_korr/sin(phi)) - (pi*(D_val(i)^2)/4/tan(phi)) * (abs(LDA4(i))/sqrt(LDA1(i)^2+LDA4(i)^2)); % [�m^2]
    end


    save(path, 'A_val');
    
    

'''

ID_32 = '''
% Funtion zur Berechnung des integralen SMD mittels der Methode nach
% Zhang
% Autor:    AS
% Date:     07.01.2015
% "i" entspricht Messposition (Bsp.: r_1 = 0 mm)

% �bergabegr��en:
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
    % Pr�fen ob positives oder negatives Radialprofil gemessen wurde
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

% Kreisringfl�che berechnen:

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
area_annulus = area_annulus.*10^6;  % Angabe in �m^2

I_D32 = sum(D30_i.^3.*n_flux_i.*area_annulus)/sum(D20_i.^2.*n_flux_i.*area_annulus);
'''


class MLS():
    def __init__(self, path) -> None:
        self.path = path
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def writeScript(self, sc, na):
        if not os.path.exists(os.path.join(self.path, na)):
            with open(os.path.join(self.path, na), 'w+', encoding='utf-8') as file:
                file.write(sc)

    def run(self):
        scripts = [D_A_FOR_PY, ID_32]
        names = ['D_A_for_py.m', 'ID_32.m']

        for script, name in zip(scripts, names):
            self.writeScript(script, name)
        
        return self.path


if __name__ == '__main__':
    mls = MLS(os.path.join(os.path.expanduser('~'), 'Atomizer Toolbox', 'global', 'scripts'))
    mls.run()