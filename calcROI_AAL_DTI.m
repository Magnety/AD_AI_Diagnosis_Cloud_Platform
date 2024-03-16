

% �����ͼ����Ҫ�Ƚ���APCP����
function calcROI_AAL_DTI()
P =  '/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii,1'; % ѡ���ļ���
tic
if(P)  
    P = cellstr(P); % ���ַ����͵�Pת��Ϊcell�ṹ������spm_vol�õ���VҲ��cell���͡���Ȼ���ǽṹ�������͡�
    % ��cell�ṹ��Ԫ�ر�׼�� 'D:\01.PPMI\test4\1.nii,1'ת����'D:\01.PPMI\test4\1.nii'
    inputFiles=cellfun(@(x) x(1:end-2),P,'UniformOutput', false); 
    ROISignals=[];
    for i=1:numel(inputFiles)
        [pathStr,fileName,ext]=fileparts(inputFiles{i});
        % ����aalģ���116������
        tarSpace=inputFiles{i};
        reMaskPath=[pathStr,'/ResliceAAL'];
        mkdir(reMaskPath);
        reMask=[pathStr,'/ResliceAAL/ResliceAAL.nii'];
        mask='/Users/liuyiyao/Downloads/MRI preprocessing/aal.nii';
        method=0; % near��ֵ
    %     method=1; % Trilinear �����Բ�ֵ
        % ��mask->tarSpace��������ΪreMask
        y_Reslice(mask,reMask,[],method,tarSpace); % mask����Ŀ��ռ�(tarSpace)��ά�Ⱥ�����һ����[]��vox,����Ҫ��д�ˡ�
        outputFileName=[pathStr,'/AAL_ROI_116.txt'];
        ROI=my_extractROISignal(inputFiles(i),{reMask},outputFileName,'',1);
        ROISignals=[ROISignals;ROI];
        rmdir(reMaskPath,'s');
    end
    xlswrite(['/Users/liuyiyao/PycharmProjects/ad_diag_sys/ROISignals_AAL_ROI_116','.xlsx'], ROISignals);%hzw��������ȥ�ģ�Ϊ�����ɶ�Ӧexcel���
end
toc
end
% ����ROI������Ҫ�õ��� unique find mean �Ⱥ���

