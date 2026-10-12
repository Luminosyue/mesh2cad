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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/963c5f8b81c045fcab90387bf3aa5143/part_003.stl', 'relative_path': '963c5f8b81c045fcab90387bf3aa5143/part_003.stl', 'source_sha256': 'fe524c194840bbc388a4720b10c367385a7d33c744bf4921787ee4c042278cd8', 'input_faces': 348, 'input_vertices': 197, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17639446258544922, -0.49999991059303284, -0.17422910034656525], [0.17640914022922516, 0.1102786734700203, 0.2263409048318863]]}
GEOMETRY_BASE85 = 'c$}r032+ou8pj_A7$m3=BA}?WMhq$<5^e<=2nccu7;c6m5ipRDAOSfX!lfd2ARt$VLkL$S5G08(lW^z?9^hKb>dMZpu8NjNQMDGXy1Vn<`*qUYnXTH|ozz$VU;p#v_4kf`-P4sJ{iAEg3;nrQG#*}9a3f9#8TCcHn3I|{d)nmG?A9|g=hYGolrKNFZWuIT;E++Z#2hg{aY}0T<gCOlM&c7`of2CaiD?;Gv$H17oRE<<B~|);CZ=bnhW+fR6Ejo8$1NZ0+_9CB^k6Gvq47U{>d6|K=A93O#cVh1&q|{%tqnx*{f{M-c9(iJ<D5GF*T1xXv|?qz;rsA|+oqh9`N8PIGtPX`EhjhN@T>B#bbV9iTTR<lsN<L>AE^Ay(zJlX_uGEio)VQ`QeXMzvexgb_P+mqk2>$11*he4sNtyh)bG9i&|fdQ{1+cOC6A4i(JEhz&d+fAp=Y%3Pr820m7o8cYDbLp<ZsfxogaGpt8#VBcm|hWSI4$5@Wor1@5p>#&L*8tzx+2^><&15fp31Z__WHuzNk!%6XR*l6YALZP1`TYd0Wlngs)G!=JAW@B~IU-7jyRNV(A-`4=P{8>GAZRy|_K#@PmxAulc06T=`Gyajuci_}lqn{J@jW`o*umoCr94yMF(izn@ceUg%Y##*g)2?7L7LaQHra>#5JqsCh|?QNK5tUvp9Mp@72=+Vk6ZPlYR=`K^&}&oB8R=He08I$xN*H{kHA)_KwXfSRu}4b|^0=27(gN!N`ZTB?0xbC&9_x#r3)b<FsO>aEcA;aiNq^=sJ~S3cukBcJiN^Tp|RcdGijMwP4Mm7l5W*=(Jwe5-y!StQ?InxuUHlDg-eeyCP^<y#$&x!cK^qI_d!D_4FHKeTVPD_?9ptbE_B-sdCv;=4Jne7k<%^%*Wdgl{Dbbl2H>r1FjTk|X+|zV7x#ZL2&|o#uc7<(qMjxY{u)KP-<lKK^=_%Oj1C$oPwE{EdpD9V-9Fc-3F?i!_&S+*qvq;E0|sUv$&`4K8l)Zs)=hUC+@TF5majkGg)-(|+g2)%EF{x?TC9<;mAhi|Xst-*9k6M88Gow9~KJXTF+U<n*idrQ+e0-6QzEm0$fXk{^2c`~|0P@2ghw;!0=x_P%PIx^dB&FY4<3!R&s#)Kw4rMsU;6w_WFD->??6JMPT4_YGgky0fl)_Kh0(>>GA|Fzw@AYW;bxYuoo;*H!tR>$)o6b6xw38tqlSXP>cs?>^(Z`p%K=qUJtk``&%byj(}!AH4gj?R)pts(jDBT9xnFSIv$+)qUQ(&)dFtpErjOQqLXU`-ts(?<3axh06Ed*KFT=U#rUZ+}En|J@++h#I=*o@wD%=w(q^q2ETr>%vryEAGdw)ecbpwPhZcT=LFlY@tkn_Yn|_T4zYdjb4c*{hfk^Vc%O^#Ydja(`QGOuJKytM6ii>J>Z<XaX8WG!H2=4;dR=&)_xyvB^nKg&+-UpW=SE|Gy7nuc_)z81j@fp<_9uL){E*cyKay{*>ZPxfYoF_SthJZac-r+?&DDNpcI$Fk<rnC7yuP1yLMdak|EJHDFMePg_FPlGXxz+Irx@Ept#{-2Sy!E2->%aPwb%PW=V`8X{DXUFf5l4W2gMaDlJEPpPN8b|j$z8TT9qr`vghmMXyu0vUsk@DnYb&GZ)Tj>r~ZEXWPQCp`i(yC*z&EB{7`FgNY#-)OV{&<I5p1JPtB}Ie(-M<s!r?nwYr_$>B=`-=5C4T7nSUY<Ol04IS|SBA8&G4T}SV3)BRfC)HT1hAH=uk*Xq1qKWD8v<{r02g}Q$4_al7o_aozvMY^6xDs`QVgVzr+4z};R^@3|&yuLjz;-gc#ow?ttcEmV6FE#u}^}JZ)f_gn%xZ&!TKkJ<C*UwRE91PCu_5GaJ_RXm=dYrF!+a1XdezW6sHEwU7*W=kK*0mnIzP%pIl=t<#yl|&FZ-_d5=^yEOTDI2f;gjfHk$fZi6IG{g@fAJqZ7N;u1V6p1>s;7R_qUe5j=a9bb!5)}QrGj>Nv?J1_5DAsE{NoZz8thal5ekD-`a0=oioy1b%v5}==|=RUHz@$(_ic7+UhyQY*X%9Z(iSCZ^3RiDPM?yo)_lP>xb-l92Tqne_V9!pT?DD+8_PPCFlC_`u6$><|OEPK8?HVY$tf4t@e|DaIH^qv7>(e3jL<ne@yc3NWS=Zi>fnpuDA02|4h*J|4?^VB;Wtt?^QkKniS>x#*EVA8JkxS$+zpQk$<V5p5GnQm2cg?T3>fR>hpSi`@F{Hxw@UC<I4BZFRyRVFXQk+-QN!?-S@9infiOS_dO53_dSoXA@97Z%kv(|>#O%jLtJmorp{e|^}_~2$hcX=i?oT3S7y?bA6p~8GMm=!zj|es)UMP2`^s#7xQ4mmm`6ySLr8v}keowEegT~i2g4!14+PLM_!L@>mcb{{6KENH0zOViE(yn*Xen9-mvO#Q^ewm)ew~nf06h&KfRCU-_z3(48i3z`iyVC`A|xL~%i)9YK1ZMT5t0kg6L0~%4LuHTgEylk@Md_cV~n;Ek}b3pE@dn%Lh^P(@?P`+yca%%9)S<RN6|Onqwq1b2tEcEqX*$)_%ON;J`C?i3*i0m4s;v51Kx;khBv}%(5>(qI1ja8i?PTfBrhQ(uR!<0E8thqL+~r`dh{r~9^Qf;gSWst(PDTf{2F=~ehuD$?uR$PE72YBO86yoBm5G)6kP)^g>%t7IFGT&B_zK{NcN*EU_ZPJeFa_yzl^SjUxqiKTi{LbZgeNS8!kj&gA3t3=mvNXoR6-A^Wj&~m*7|7<>*p)IlLIng>xB;#f0Pqs2^ScFGQEY%jo|?Lh>qf6TFE&uOcMxLJQ$S`nijcyc*4i^Xc1aLh>SXIlP=cEJ7E+@?MbR=t~a1)ED4I@M?6v<6QHpOX@sFo%86^0{U;?cO=h2SHY{umz*4qXTp(yPJyMS!ndQ13CZ^pl6w=9Q_xg61)e}iUWZPB*THMiXW+H)cr+Ov5BEY7;9hVuN8QZ`$+gkOaBa8_dOutTz6<RQ-v#$UQ{WW()`yV%Bq8}(bRGOGT#2rQE8z-sJX`^%p}pWVxF^~S?g=+SYr~D;D6|e71xKTI!O?I$+6V4K-{Lu!Y`1SX62s9V9L)*IcM~nh=?gzaNFIPD!UNzzgyaX&=J12?y=W8oUigl17~yyz94!gS1JVAl)DiGNcqk!x6gm!;It?BLPb4JIKxe~Jv)~zUCLuW;&4#5;h0|dlA$cS^79N5QN5{g$;pym9cshIr&4#n7;|wABEIJ#WP2bKElAlAz!Q&XO=LpID(Ee~gxB>bA+yK4@HQ;;TIJ7Ao2iFhBEkb@-5TYJhAFc=AiZ+FBh3`ZS_)hpfv?Y8W{17@2eh40n4uuE9!_ZOiFnA0)5gr3iMrXj2;S4kr&VXm3>F_LgChCJ{!jsUE@FaM&s9sN_3CT|jeGN(-fDVDB4j0wetYrJTmfRPeE~>A6$@U&4ISoA{s`oU>73f(}y$4FJM4uDYd#2=P(SD+OkCpr++CWtA$&%&X6^+(H8^BWUfu+X5wcr@EJ{$wrMQ?`d!m;Qru+%$XsZHQmxFOmcmU=hb5WWrV3rlSTOO1kWg9RE5N7EmH#=tSuZGR-+gvP?L)NvDf8!S+H+%X&vhob`_If;<mmXO?rkldP(+=`I=2qF1VLh@sT<aUJQ_Jrh4gyhbI<i`ogUC@qj7q|x@*+e_QCfprOg1f`r(6(?lxGUNQ?g~E<jv@VPMa4(|r+*=;{`l48Isc)^`<L$5D9*p^5MCfvFI9&0ucPKJD*Piij~?=gNBkQQ2VB_'

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
