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

    % NEW
    res = Ttime .* LDA1;
    sum1 = cumsum(res);

    for i=1:length(D)
        D_val(i) = (4/pi)*((ls_korr*sum1(end))/(ls_korr-cos(phi)*sum1(end)*abs(LDA4(i)/sqrt(LDA1(i)^2+LDA4(i)^2)))); % [�m]
    end
    
    % Ab hier ist D_e in [�m]
    
    for i=1:length(D)
       A_val(i) = (D_val(i)*ls_korr/sin(phi)) - (pi*(D_val(i)^2)/4/tan(phi)) * (abs(LDA4(i))/sqrt(LDA1(i)^2+LDA4(i)^2)); % [�m^2]
    end

    save(path, 'A_val');
    
    

