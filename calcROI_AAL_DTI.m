

% 计算的图都需要先进行APCP矫正
function calcROI_AAL_DTI()
P =  '/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii,1'; % 选择文件夹
tic
if(P)  
    P = cellstr(P); % 将字符串型的P转换为cell结构，这样spm_vol得到的V也是cell类型。不然会是结构数组类型。
    % 将cell结构的元素标准化 'D:\01.PPMI\test4\1.nii,1'转换成'D:\01.PPMI\test4\1.nii'
    inputFiles=cellfun(@(x) x(1:end-2),P,'UniformOutput', false); 
    ROISignals=[];
    for i=1:numel(inputFiles)
        [pathStr,fileName,ext]=fileparts(inputFiles{i});
        % 计算aal模板的116个区域
        tarSpace=inputFiles{i};
        reMaskPath=[pathStr,'/ResliceAAL'];
        mkdir(reMaskPath);
        reMask=[pathStr,'/ResliceAAL/ResliceAAL.nii'];
        mask='/Users/liuyiyao/Downloads/MRI preprocessing/aal.nii';
        method=0; % near插值
    %     method=1; % Trilinear 三线性插值
        % 将mask->tarSpace，重命名为reMask
        y_Reslice(mask,reMask,[],method,tarSpace); % mask会与目标空间(tarSpace)的维度和体素一样，[]是vox,不需要填写了。
        outputFileName=[pathStr,'/AAL_ROI_116.txt'];
        ROI=my_extractROISignal(inputFiles(i),{reMask},outputFileName,'',1);
        ROISignals=[ROISignals;ROI];
        rmdir(reMaskPath,'s');
    end
    xlswrite(['/Users/liuyiyao/PycharmProjects/ad_diag_sys/ROISignals_AAL_ROI_116','.xlsx'], ROISignals);%hzw后来加上去的，为了生成对应excel表格
end
toc
end
% 计算ROI可能需要用到的 unique find mean 等函数

