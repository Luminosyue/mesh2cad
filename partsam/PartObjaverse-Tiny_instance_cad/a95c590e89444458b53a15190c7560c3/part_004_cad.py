"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_004.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_004.stl', 'source_sha256': '27dc7cf08b3ddd4aabddc2ce8bca3fbf67deb6057c72a716a228e3427c64eb79', 'input_faces': 288, 'input_vertices': 174, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.21503835916519165, -0.1736467480659485, -0.04685288667678833], [0.28872430324554443, 0.08401364088058472, 0.34941425919532776]]}
GEOMETRY_BASE85 = 'c$}q~2~>`08^<3@$dZsOO}y696eCHp^fKAEY{_0!LP(J;jVC)JyCO*>vS%B@@LI+)#@L6keK8AT>|@3l%lV%B`v05W=J?L}&iB3NT<8D0|K0DsT=(@XUICqo6m`(>siD1&ym#h;y{4%stvP71VbSA;4-Jc{KRRk+A<bTV^~uwvU3+&4=vzpO)h4@yhQ$nxcJVd2G!OT2aW}bykBJ@^9Wr|GnCQ?j<+lxqj0rRRn23<5Fr)3-u!)zusZl+5Q@rVa{FF47pa;)7dqk}zcf(hrK^^A!DLqh1d`q7q@VlO0A%3fsUrT$g>q*foRTGu3&$xa@wRJmR_#^Hwlm5x`#kZ`yigD&yQl)>JTxsjyH`^nAZ1!r=<SX#~mVF`Z_4krR6Bgk61K#fw?bs+ybn_hefoJ!MPP1Jkx?vLhOa2(AS44)4n-K%wwd!usClO1;-%%dEN0nWo6=ts$b-Hju{ysH6N7_4kq)YqpDe<+CCz!YN;OV0F+u&cQj(xdT+93MFdie3LvPDx*VqXEnF@C+s{nEbcnkntI1K}^|f_0wwY?|o1Uyh58zlm{{I?KMax<A6dpdYZ#kACh3{N2xyhZ0Wlq6b!qug7<QpL1=awXda(K^}rKxc=qvZQtw=J)9utrROfdIQQIkq8>UYiu%<=|63Uctj|$j;tbzCW`BXa`8vRVc{j)UytMfx;P*X_eCpLE$T(B39TR<iBd5T*cR3CJTxImH`VRa0{jm62^E$}ejmRXdt1bK&hxQdXud_|z_enz@QajF)aedw&#d<0pC{VZFuf*50AAVtdUize?@Z){=TIW-*xgX;!_eb6WbC!xGEr!48xBUg`bKNKKx4+m|pgzaDVtkv^d#v-X&wpr<cH<#?3)IQpAK^Pa+f^VBSC7Gef8h)3`qZP7;6F{+V}0&g_=QcPJ{L3OI`@iB{GhKb_4c#&Q_We@_J5di<U{@=$GHXi--_HJZM(!ZM?T~~*gWNfeo~Xg1;%OGarX!3&GY{`@2?4aKe(?vKW|^RD}N)pXxC1q>BSN+OS{-y_^IvIioUvjLA2&>_)ErRD-Di%f&O0}hM!_D{Y}r@E=jx2WB4UbNj@!6H!n(ic$IUaogZ!yzj4+TX)kbs@83=GY5C{{#&M|)-}$)gH+TN&tJ1FC4Ssgu+#@ot&sk|V905PH(<&L~OeE(0ITik4r_HK=x_0%1wEJbi53=2+)cj;2)^qJ3{QYHCE7eC=!G4p@z>nx5*R5%Bv2UfFb_xF5&az*#+h3S>?REHnZjt+i-k>$wzIUP5CoPx$D^s!GJ8$5>@RvLUZ)=YIy1awG;@Co2&wD@g_u%|d&v1_C27D*&V<q4RT#J`+%1_2Qp0tB+@d#JzF+Zq#UfS(F;BT+HUGltP0`ky!68zvg!&HCE03YltcqV);bQ9{YHrDxaHvAbU<oZnSei?Ppeg*uN8uFi!c}m({(%_dkE_pEhybXEw+6g~5RO;CDItuI0InQy9r^|k`9v~0N-@(ra+%Ee%dh0ayc@uub^?5SB#f<Sw-G<+O_iWWa*d`PCb^0Ctir-dB-Y$>C_=#`epT>1)c|9I^>ud{M^mvNY+mWZ}-@PpSUJ0A!yzZAmep2n>JM@$HjC7x}=pR=OepHU!XM+bf_*&Y56~)(|AC>!UdS({#7UqWjX+d&7P4B+|>pR~c{>dkq^1X-InD=cs{1qi<O8@xFILE9+_?A|E<=m5s!*90+^R{gy^IEbdU|!p7^v~Kl9p_aUb#i1U{0q%eq@GRj$aBv<@XzkpD*GD#5Z9^i3HaY^O2NF@7{~D|_(3r<<QyBBaqb;&!9P6(`M*^d>+JOaenW4$&zrB?pOkj#hw#l+WnR7UWYmM_Q}}c4%6-=SS6Qrc+8^-CkHz)t>?qffKBbV%uU|=)JeZpg!@20iv96-gcn*zrK)y6v-Y<RRd6eF%%vaJrSO)%#=ylTnw_#}4v%~m*{DkLb_eRI19SmO!ikL0=d3_jl66yfok|FN{xmDWXTxwQ_ALk?QPnPrUQV;qK6UHA`U-Dzw<#|T>ovDfbhwjUJo9Uv4eob1yH+jZM|9$Hu&-yp5;YSpmDSEdp&MTx1zBj0$Jm1at&SE_&?YYi?UXss7pGltegM;Avw3YWC%hStpUi!-r_^xU5Q9loGE<X<CyfL_M+@6E_`JDL+NXL6o_CQ>}!y@3fFR@Va<K7i{bByD86_xYKb-aXie>W3;E&Y)Afjx0vk)Px5853oEJ=+H7UST2n`{m;OcKQujj~<c)KgAvIZ9kMkeQr%=KE37r+vL#%?X#OP{-^dB$K|5br#^iv{@!m3-uoTXQJ2x%;TMUOy3$`~Vm(!M!M}6qu;gdk#AB#~eegXx;ytL>D5)#$lN_$+jl7R)#meIx`yGXE|Fzsta?eF${XNceoC=sXaD<$%{wMSIC=Tzj_54s*;~$`ZaaYuHXf)2(=@I&$Ogt##c(=p#c;zwo>n!gnxd|)KZ_;!4EsDx}ySesTJV#EJMLj+bk#S6CpW`_`x&r*2rz8*h>XVqaPDSh^#}@04@s&E!msf^Ax_%bwp#{Ewj=tS7dCxSzibK6Qnc#arTQBoE-^BWoJn_Bi&7{AcF(2363@`NWn=W~<{9+^P*FWa-b9<1y-&#ib;~X2df?qH8h|GJs6wd2=fAP&PN6GuLB_$X8-8BIH5A~Dr&8u&teoDt;J<G?)d%k7!Pq-fAC&IsEk8|mN6?NNk9>(!?mFH&qt}yg-Sq)#`^rehbE)4lBl7_z@s(^ExH(J)O{|ml0=U2JUq~E`e^YYmX|AtA%$sIFR>O?Po82$lA+&66O`CO;(I!%1jp!HbimE-WIr%4{t-P+4_sxSFge9O%{sPnQ@B|rM{w^--9G2-iw+8{sUC&~RlZ|W`AySYf*w|)Tyehs;^WlN}Lr%J$h+G!42c!<?cA@T=J`&&Q!Q^;_y|LUg@PamKE_otB6#u`={v4Np@8FeaIX)Jjec`ifoY-$u)>2UIF@-*sD@-*^9>Ok^D@;HX#Q4Ga>jc7}4MIA_PMea-;O72YVLLE--LJp!vk%P$Hsj=kl<U!P_WTlbhLF67rw5E=yMv|4zAS<0i9#0-gT}W2Cm^_j^mb#ogmK<Zm=hQUna&j7Z3w1qtGj%I<J$Wm6BXuo#BRP|rPFA{_oJrn9-9X+(&7y7~XOUM?mywmuC9fhcWhhRe&L%6JMou9wpiU$&ASY1AkrT*M7>Ylmjv{w5BE*OR48`Hp2yz7bhEqq8!^yp=eaU$>-J9By+?(8$>PuGYM^<@WXGAJv9doSK8DK;QBU%{oDZis?GSrB{)RE-8eT}AeBKvVZAFFv4CmJ!yDp!ibs1f9*8m`Ia)Mn)7WVI)=hU=;wwGFu)SzV(UMy#+pcg3@)3&^?=GmS`QD4u7;bR&|Ch^H<g$CD>h7m+8ECs5~+=W)yl48>!N2&4|9&Lq#|nuakH2UFw7N~6ia<bDjry{IF|y~y3DL&)989jX1vO8byIlG`&B`!f{x)NtmiUP7on$syzjhT<@4A95eg7sgPWR~w2Gs6({;Yi$V6ZwU93cWsW~nU3K8XHnzGv&eb%pm-HkCo4_X^6wjp)jeh#HI<r7Ryt41zm61VQWuexF46MuZ;CfkleGMMqhfXM+)Q0VO(H9uPF_Qvui?I}G=@5z977&Ujo0$;`HDwUCzF*<(DI)biU(82kn?I+acgQ1Y9P4>c@T9NS!uAA|GZP&o!U>!e^x4PL+wRwL+(QDrsY426?dj~)bgL*id#|JYx&Q5#m%Vx<YwfS)E4BHWM772buTMoL?I&zGZd>&4I?TW@exCDIciyQIdVyADRN1&4b_fpL$;+>B-@hhsV1^L*~y41MpQ7OCe?{tlk7q@kzL637>a9CE0SxIt5NO9)yR(2Qe;PRd1_g5d2%IcWpX8Qb!rWAb#fge+^DY98e~^;E$T<)TI8w>#SYYRWCwB?YDsb#atW#pxdgcw)s|e0T%2l8E>12@bs{_QY)Uf}=Y13xrdHAN>rJt$!J<@WY8A3Gxh}OPxi0x*stfsJvOBdN*_~XUq1c03o9sbuK&?h@KyFBNBsU~`QOlE6cv|)Gv>M0LYA#Q!^(g*?p|}x4abt$!CJe>iR4=j@*WgX9MD`{(p;osVr#i=0TE}XxI-EbRM)TI=#x>Tbx>Mb(^6bWQQ0i)RF0MQ`rM1WboeC9pDDt2FD?R_C%Z<tUKi2>G&4T~zwEm`@aS{CekI;ZlHma_T;wvl<kPd3++P?w7g-l`'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
